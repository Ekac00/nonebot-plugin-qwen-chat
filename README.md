<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# Qwen Chat

_✨ 一个bot可以主动发送消息、表情包或自主让长消息分段发送的qwen大家族对话插件，让你的bot更拟人 ✨_


</a>
<a href="https://github.com/Ekac00/nonebot-plugin-qwen-chat/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/Ekac00/nonebot-plugin-qwen-chat.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-qwen-chat">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-qwen-chat.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">

</div>

> [!WARNING]
> 你正在DEV分支预览项目！
> 本分支可能会有亿点奇奇怪怪的bug
> 回到[回到main](https://github.com/Ekac00/nonebot-plugin-qwen-chat/tree/main)

## 📖 介绍

现有大模型对话插件配置难？回复慢？不能发图片？不能自定义角色？
**Qwen Chat**来帮你！

本项目正处于开发阶段，完成时间待定

## 💿 安装
<details open>
<details>
<summary>使用PIP安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 输入安装命令

    pip install nonebot-plugin-qwen-chat

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_qwen-chat"]


</details>

## ⚙️ 配置

`
qwen_api_key="" # 必填 阿里云百炼API密钥
qwen_model="" # 必填 模型名称（目前只支持阿里云百炼平台模型）
user_prompt="" # 必填 用户提示词
bot_bot_name="" # 必填 机器人名称
emoji_dir="" # 必填 表情包目录（此版本无用）
debug_mode= # 可选 开发模式（输出详细日志）
`

## 🎉 使用
直接发送包含{name}的内容即可唤醒

## TODO LIST

 - [x] 完成基础功能（支持大模型主动换行的对话）
 - [x] 使用异步请求OpenAI Python客户端
 - [ ] 让大模型能够发送表情包和网络图片
 - [ ] 永久记忆（指本地保存）对话上下文
 - [ ] 全模态支持（需要等Qwen Omni）

## 参考的项目（仅参考逻辑）
[nonebot_plugin_random_reply](https://github.com/Alpaca4610/nonebot_plugin_random_reply)<br>
[MaiBot](https://github.com/MaiM-with-u/MaiBot)

<!--## 二次开发声明
任何基于本项目的修改版本需满足：
- 保留原作者 糕蛋\Ekac_ 的版权声明；
- 不得删除或隐藏原始项目链接；
- 不得声称修改版本为独立原创作品。
-->
