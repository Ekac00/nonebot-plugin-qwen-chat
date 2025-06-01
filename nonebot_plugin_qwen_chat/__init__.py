import asyncio
from nonebot.adapters import Event, MessageSegment
from nonebot.plugin import PluginMetadata
from nonebot import get_plugin_config
from nonebot_plugin_alconna import AlconnaMatcher, on_alconna, Match
from arclet.alconna import Alconna, Args

from .message_handler import qwen_handler
from .config import Config
from nonebot.plugin import PluginMetadata


config = get_plugin_config(Config)


__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-qwen-chat",
    description="一个bot可以主动发送消息、表情包或自主让长消息分段发送的qwen大家族对话插件，让你的bot更拟人",
    usage="消息中带[NICKNAME]即可自动唤醒，也可以设置监控所有消息",

    type="application",

    homepage="https://github.com/Ekac00/nonebot-plugin-qwen-chat",

    config=Config,
)


# 定义命令格式
chat_cmd = Alconna(
    f"#{config.name}",
    Args["prompt", str],
    help_text=f"与{config.name}对话（可包含{{name}}占位符），支持文字和图片输入"
)

# 初始化消息处理器
chat_handler = on_alconna(chat_cmd, priority=10, block=True, aliases={"千问"})

@chat_handler.handle()
async def handle_chat(
    matcher: AlconnaMatcher,
    event: Event,
    prompt: Match[str],
):
    await chat_handler.send("正在思考中...")
    """处理群聊/私聊消息"""
    user_id = event.get_user_id()
    is_group = event.get_event_name().startswith("group")
    
    # 获取消息文本
    message = prompt.result.strip().replace('{name}', config.bot_name)
    if not message:
        return
    
    try:
        # 调用Qwen API获取回复，添加10秒超时
        response = await asyncio.wait_for(
            qwen_handler.call_qwen_api(message, user_id, is_group),
            timeout=10
        )
        
        # 处理流式输出
        if segments := await qwen_handler.handle_stream_output(response):
            await matcher.finish(MessageSegment.text("\n".join(segments)))
        await matcher.finish(response)
        
        # 添加表情包
        emoji_keywords = ["开心", "谢谢", "生气", "讨厌", "惊讶"]
        for keyword in emoji_keywords:
            if keyword in response:
                emoji_url = qwen_handler.get_emoji(keyword)
                if emoji_url:
                    await chat_handler.send(MessageSegment("image", {"file": emoji_url}))
    except asyncio.TimeoutError:
        await chat_handler.send("请求超时，请稍后再试")
    except Exception as e:
        await chat_handler.send(f"处理消息时出错: {str(e)}")