from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import os
import glob
import random

from tools.wx_publisher import WeixinPublisher
from utils import utils

class ReadTemplateToolInput(BaseModel):
    audit_file: str = Field(description="审核修改后的文章")


# 1. Read Template Tool
class ReadTemplateTool(BaseTool):
    name: str = "read_template_tool"
    description: str = "从本地读取模板文件"
    args_schema: Type[BaseModel] = ReadTemplateToolInput

    def _run(self, audit_file: str) -> str:
        # 获取模板文件的绝对路径
        template_dir_abs = os.path.join(
            utils.get_current_dir(),
            "knowledge/templates",
        )
        template_files_abs = glob.glob(os.path.join(template_dir_abs, "*.html"))

        if not template_files_abs:
            raise FileNotFoundError(
                f"在目录 '{template_dir_abs}' 中未找到任何 HTML 模板文件。请确保模板文件存在。"
            )

        selected_template_file = random.choice(template_files_abs)
        with open(selected_template_file, "r", encoding="utf-8") as file:
            selected_template_content = file.read()

        return selected_template_content


class PublisherToolInput(BaseModel):
    appid: str = Field(description="微信公众号 AppID")
    appsecret: str = Field(description="微信公众号 Key")
    author: str = Field(description="微信公众号作者")
    img_api_type: str = Field(description="文生图平台方")
    img_api_key: str = Field(description="文生图平台方 Key")
    img_api_model: str = Field(description="文生图模型")


# 2. Publisher Tool
class PublisherTool(BaseTool):
    name: str = "publisher_tool"
    description: str = "从排版设计后的文章中提取内容，保存为最终文章，并发布到微信公众号。"
    args_schema: Type[BaseModel] = PublisherToolInput

    def _run(
        self,
        appid: str,
        appsecret: str,
        author: str,
        img_api_type: str,
        img_api_key: str,
        img_api_model: str,
    ) -> str:
        # 自定义工具接收上一个task数据有很大随机性，这里只能从保存的文件读取数据
        tmp_article = os.path.join(utils.get_current_dir(), "tmp_article.html")

        with open(tmp_article, "r", encoding="utf-8") as file:
            content = file.read()

        # 提取审核报告中修改后的文章
        article = utils.extract_modified_article(content)

        if article is None:
            # 如果没有找到 html，则返回错误消息
            return "未找到修改后的文章。"

        # 发布到微信公众号
        try:
            article = self.pub2wx(
                article,
                appid,
                appsecret,
                author,
                img_api_type,
                img_api_key,
                img_api_model,
            )
        except Exception as e:  # noqa 841
            pass

        # 保存为 final_article.html
        with open("final_article.html", "w", encoding="utf-8") as file:
            file.write(article)

        return "文章已成功保存并发布。"

    def pub2wx(
        self,
        article,
        appid,
        appsecret,
        author,
        img_api_type,
        img_api_key,
        img_api_model,
    ):
        try:
            title, digest = utils.extract_html(article)
        except Exception as e:
            print(f"PublisherTool 执行出错: {e}")

        publisher = WeixinPublisher(
            appid, appsecret, author, img_api_type, img_api_key, img_api_model
        )

        image_url = publisher.generate_img(
            "主题：" + title.split("|")[-1] + "，内容：" + digest,
            "900*384",
        )

        # 封面图片
        media_id, _ = publisher.upload_image(image_url)

        # 这里需要将文章中的图片url替换为上传到微信返回的图片url
        image_urls = utils.extract_image_urls(article)
        for image_url in image_urls:
            local_filename = utils.download_and_save_image(
                image_url,
                utils.get_current_dir("image"),
            )
            if local_filename:
                _, url = publisher.upload_image(local_filename)
                article = article.replace(image_url, url)

        add_draft_result = publisher.add_draft(article, title, digest, media_id)

        publish_result = publisher.publish(
            add_draft_result.publishId
        )  # 可以利用返回值，做重试等处理

        article_url = publisher.poll_article_url(publish_result.publishId)
        if article_url is not None:
            # 该接口需要认证
            publisher.create_menu(article_url)
        else:
            print("无法获取到文章URL")

        # 通过群发使得文章显示到公众号列表 ——> 该接口需要认证
        media_id = publisher.media_uploadnews(article, title, digest, media_id)
        publisher.message_mass_sendall(media_id)

        return article
