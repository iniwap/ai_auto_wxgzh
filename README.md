# 微信公众号自动发文
基于CrewAI，自动获取各大平台热点，使用AI生成文章，发布到微信公众号。

## 项目背景
为了学习CrewAI，特开发了这个小项目。最后才发现公众号限制巨多，有认证的微信公众号的可以更好的发挥这个项目的作用。

 🤝 **欢迎交流，fork，来点star更好！**  🤝

## 基本功能介绍
- 自动获取各大平台热门话题
- 自动根据话题生成文章，CrewAI多个角色共同完成
- 自动发图文消息到公众号

### 个性化功能

为了更好的满足各种需求情况，通过配置文件（`config.yaml`）来完成

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

## 问题定位
如果遇到没有发布成功或者没有生成final_article的情况，又找不到问题，请临时更换下CrewAI版本：
```shell
pip  uninstall crewai
pip  install crewai==0.102.0
```
**此版本会输出过程日志，仍看不出问题的，可将日志提交Issue**
恢复到最新版本：
```shell
pip  uninstall crewai
pip  install crewai
```

## 模板发布效果预览
经过反复的微调，已经完成的模板效果如下：
- **template1**: https://mp.weixin.qq.com/s/9MoMFXgY7ieEMW0kqBqfvQ
- **template2**: https://mp.weixin.qq.com/s/0vCNvgbHfilSS77wKzM6Dg
- **template3**: https://mp.weixin.qq.com/s/ygroULs7dx5Q54FkR8P0uA
- **template5**: https://mp.weixin.qq.com/s/pDPkktE_5KnkQkJ1x2-y9Q
- **template6**: https://mp.weixin.qq.com/s/7F_Qdho-hzxeVV6NrsPmhQ
- **template7**: https://mp.weixin.qq.com/s/ug7NseZDziDMWBVwe3s1pw

*有兴趣的可以继续微调（如边距等），上面的模板可以比较好的显示在微信公众号上了。执行代码时，选择使用模板，生成的文章会自动选取填充上面的模板发布文章。*

:smile: **调整这些模板花费了大量时间，麻烦关注下公众号** 👆
 
## 其他说明
~~由于不熟悉微信公众号开发，哪位知道如何正确的使用“position: absolute;”，麻烦提一个issue 或者PR给我。
这个很必要，因为生成的模板都使用了，浏览器显示正常，但是发布到微信公众号，就变成了垂直排列，无法作为背景。整体效果差太多了。~~
### 经过分析，发现以下问题：
- **发布文章后，微信会自动移除position: relative 和 position: absolute等 ，必须通过其他方式实现**
- 微信公众号支持animateMotion，不支持animate（经测试只支持透明度变化动画，也不全是模板1的动画没问题，这个需要继续测试）
- 调整好的模板，效果虽然不能完全和原来的相比，但是总体还不错（有背景装饰、有动画）
- 不支持button，会被自动移除
- 会自动移除 background: url('data:image/svg+xml;...)

