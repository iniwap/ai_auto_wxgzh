# 微信公众号自动发文
基于CrewAI，自动获取各大平台热点，使用AI生成文章，发布到微信公众号。

## 项目背景
为了学习CrewAI，特开发了这个小项目。最后才发现公众号限制巨多，有认证的朋友可以更好的利用这个项目。**欢迎交流，fork，来点star更好**。

## 基本功能介绍
- 自动获取各大平台热门话题
- 自动根据话题生成文章，CrewAI多个角色共同完成
- 自动发图文消息到公众号

### 个性化功能

**为了更好的满足各种需求情况，通过配置文件来完成**

- platforms：可以设定每个平台的随机选取的权重
- wechat: 支持配置多个微信公众号
- api：支持配置多个大模型平台，使用哪个修改`api_type`即可，只需改成你的api_key，其他不用变
    - model是列表，可以选用一个平台的多个模型中的一个，修改`model_index`即可
    - openrouter的api_key也设计了多个，可以用来切换多个号（如果一个用完了）
- img_api：生成图片模型，主要是用来做公众号封面图的
    - picsum: 由于生成图片消耗太大，这里提供一种随机图片方式，修改成这个`api_type`即可
- use_template: 目前只有Claude 3.7有比较好的模板生成效果，由于无法直接使用（有API付费的当然），这里特别设计是否使用内置模板（每天可以免费到POE生成模板放到`knowledge/template`文件夹下）

## 运行方式

需要先安装所有依赖。

```python
pip install -r requirements.txt

cd ai_auto_wxgzh

python .\src\ai_auto_wxgzh\main.py
```
