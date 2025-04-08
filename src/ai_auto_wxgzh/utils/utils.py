import re
import os
import random
import warnings
from bs4 import BeautifulSoup
import requests
import time


def get_random_platform(platforms):
    """
    根据权重随机选择一个平台。
    """

    total_weight = sum(p["weight"] for p in platforms)

    if int(total_weight * 100) / 100 != 1:
        warnings.warn(f"平台权重总和应为1，当前为{total_weight:.2f}，将默认选择微博", UserWarning)

        return platforms[0]["微博"]

    rand = random.uniform(0, total_weight)
    cumulative_weight = 0
    for platform in platforms:
        cumulative_weight += platform["weight"]
        if rand <= cumulative_weight:
            return platform["name"]


def extract_modified_article(content):
    match = re.search(r"```(?:html)?\s*([\s\S]*?)```", content, re.DOTALL)

    if match:
        return match.group(1).strip()
    else:
        return content.strip()


def extract_html(html, max_length=64):
    title = None
    digest = None

    soup = BeautifulSoup(html, "html.parser")
    title_tag = soup.find("title")
    h1_tag = soup.find("h1")

    # 标题优先级：<title> > <h1>
    if title_tag:
        title = " ".join(title_tag.get_text(strip=True).split())
    elif h1_tag:
        title = " ".join(h1_tag.get_text(strip=True).split())

    # 摘要
    # 提取所有文本内容，并去除多余的空格和换行符
    text = soup.get_text(separator=" ", strip=True)
    text = re.sub(r"\s+", " ", text).strip()

    if text:
        # 如果文本长度超过最大长度，则截取前max_length个字符
        if len(text) > max_length:
            digest = text[:max_length] + "..."
        else:
            digest = text

    return title, digest


def replace_image_urls_with_array(html, new_urls):
    soup = BeautifulSoup(html, "html.parser")
    img_tags = soup.find_all("img")

    for i, img_tag in enumerate(img_tags):
        if i < len(new_urls):
            img_tag["src"] = new_urls[i]

    return str(soup)


def get_latest_file_os(dir_path):
    """
    使用 os 模块获取目录下最近创建/保存的文件。
    """

    files = [
        os.path.join(dir_path, f)
        for f in os.listdir(dir_path)
        if os.path.isfile(os.path.join(dir_path, f))
    ]
    if not files:
        return None  # 如果目录为空，则返回 None

    latest_file = max(files, key=os.path.getmtime)
    return latest_file


def extract_image_urls(html_content):
    patterns = [
        r'<img[^>]*?src=["\'](.*?)["\']',  # 匹配 src
        r'<img[^>]*?srcset=["\'](.*?)["\']',  # 匹配 srcset
        r'<img[^>]*?data-(?:src|image)=["\'](.*?)["\']',  # 匹配 data-src/data-image
        r'background(?:-image)?\s*:\s*url$["\']?(.*?)["\']?$',  # 匹配 background
    ]
    urls = []
    for pattern in patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        urls.extend(
            [url for match in matches for url in (match.split(",") if "," in match else [match])]
        )
    return list(set(urls))


def download_and_save_image(image_url, local_image_folder):
    """
    下载图片并保存到本地。

    Args:
        image_url (str): 图片链接。
        local_image_folder (str): 本地图片保存文件夹。

    Returns:
        str: 本地图片文件路径，如果下载失败则返回 None。
    """
    try:
        # 创建本地图片保存文件夹
        if not os.path.exists(local_image_folder):
            os.makedirs(local_image_folder)

        # 下载图片，允许重定向
        response = requests.get(image_url, stream=True, allow_redirects=True)
        response.raise_for_status()

        # 生成本地文件名
        timestamp = str(int(time.time()))
        local_filename = os.path.join(local_image_folder, f"{timestamp}.jpg")
        # 保存图片到本地
        with open(local_filename, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        return local_filename

    except requests.exceptions.RequestException as e:
        print(f"下载图片失败：{image_url}，错误：{e}")
        return None
    except Exception as e:
        print(f"处理图片失败：{image_url}，错误：{e}")
        return None


def replace_image_urls_in_html(html_content, local_image_folder):
    """
    替换 HTML 中的图片链接为本地路径。

    Args:
        html_content (str): HTML 内容。
        image_urls (list): 图片链接列表。
        local_image_folder (str): 本地图片保存文件夹。

    Returns:
        str: 修改后的 HTML 内容。
    """
    image_urls = extract_image_urls(html_content)

    for image_url in image_urls:
        local_filename = download_and_save_image(image_url, local_image_folder)
        if local_filename:
            html_content = html_content.replace(image_url, local_filename)

    return html_content


def get_current_dir(dir_name=""):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 拼接 image 目录的相对路径
    return os.path.join(current_dir, "../../../", dir_name)
