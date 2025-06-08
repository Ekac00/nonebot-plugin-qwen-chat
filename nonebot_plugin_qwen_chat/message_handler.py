from typing import Dict, List
import httpx
import json
import os
from nonebot import get_plugin_config
from openai import AsyncOpenAI
from nonebot_plugin_alconna import Alconna, Args
from nonebot import require

require("nonebot_plugin_localstore")

import nonebot_plugin_localstore as store

from .config import Config

config = get_plugin_config(Config)

class QwenChatHandler:
    def __init__(self):
        self.api_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.contexts: Dict[str, List[Dict]] = {}  # 上下文存储
        self.emojis: Dict[str, str] = {}  # 表情包库
        
        self.stream_buffer: str = ""  # 流式输出缓存
        self.default_system_prompt = """你是一个多模态AI助手，具备以下功能：
1. 支持文本/图片/音频输入处理
2. 自动维护对话上下文（最大长度：{config.max_tokens} tokens）
3. 流式响应输出（使用<#br>标记分段）
4. 表情包自动匹配（通过<#img;id:xxx>调用）
你的角色设定：{config.role}"""
        
        # 初始化配置
        self.config = config
        
        # 初始化localstore数据目录
        self.data_dir = store.get_plugin_data_dir()
        
        if config.emoji_dir:
            self.load_emojis_from_dir(config.emoji_dir)
        
    async def call_qwen_api(self, prompt: str, user_id: str, is_group: bool = False, images: List[str] = None, audio: str = None) -> str:
        """调用Qwen API获取回复
        :param images: 图片URL列表
        :param audio: 音频URL
        """
        # 根据模型类型禁用特定功能
        if self.config.is_qwen_model():
            images = None
            audio = None
        elif self.config.is_vl_model():
            audio = None
            

        
        # 定义Alconna命令
        img_cmd = Alconna(
            "<#img",
            Args["type": ["url", "id"], "content": str],
            ">"
        )
        
        # 解析图片URL格式
        if result := img_cmd.parse(prompt):
            if result.matched:
                img_type = result.main_args.get("type")
                content = result.main_args.get("content")
                
                if img_type == "url":
                    img_url = content
                    prompt = prompt.replace(f"<#img;url:{img_url}>", "")
                    if images is None:
                        images = []
                    images.append(img_url)
                elif img_type == "id":
                    emoji_url = self.get_emoji(content)
                    if emoji_url:
                        prompt = prompt.replace(f"<#img;id:{content}>", "")
                        if images is None:
                            images = []
                        images.append(emoji_url)

        
        # 构建多模态输入
        input_content = [{"text": prompt}]
        if images and not self.config.is_qwen_model():
            for img_url in images:
                # 根据阿里云文档，图片URL需要是公网可访问的
                input_content.append({"image": img_url if img_url.startswith("http") else f"file://{img_url}"})
        if audio and self.config.is_omni_model():
            # 根据阿里云文档，音频URL需要是公网可访问的
            input_content.append({"audio": audio if audio.startswith("http") else f"file://{audio}"})
        
        # 构建上下文
        context_key = f"group_{user_id}" if is_group else f"private_{user_id}"
        messages = self._build_context(prompt, context_key)
        

        
        try:
            aclient = AsyncOpenAI(
                api_key=config.qwen_api_key,
                base_url=self.api_url
            )
            
            completion = await aclient.chat.completions.create(
                model=config.qwen_model,
                messages=messages,
                max_tokens=config.max_tokens,
                temperature=config.temperature
            )
            
            # 更新上下文
            self._update_context(context_key, {
                "role": "assistant",
                "content": completion.choices[0].message.content
            })
            
            return completion.choices[0].message.content.replace('{name}', config.bot_name)
        except httpx.HTTPStatusError as e:
            error_detail = f"HTTP错误: {e.response.status_code} {e.response.reason_phrase}"
            try:
                error_detail += f"\n响应内容: {e.response.json()}"
            except:
                error_detail += f"\n响应文本: {e.response.text[:200]}"
            return f"调用Qwen API出错: {error_detail}"
        except Exception as e:
            return f"调用Qwen API出错: {type(e).__name__}: {str(e)}"
    
    def _build_context(self, prompt: str, context_key: str) -> List[Dict]:
        """构建对话上下文"""

        
        # 初始化上下文（已包含系统提示和用户提示）
        self.contexts[context_key] = []
            
        # 初始化系统提示和用户提示
        system_prompt = {"role": "system", "content": self.default_system_prompt}
        user_prompt = {"role": "user", "content": config.role.format(name=config.bot_name) if config.role else ""}
        self.contexts[context_key] = [system_prompt, user_prompt]
        
        # 添加用户新消息
        self.contexts[context_key].append({
            "role": "user",
            "content": prompt
        })
             
        # 保存到localstore
        os.makedirs(self.data_dir, exist_ok=True)
        context_file = os.path.join(self.data_dir, f"{context_key}.json")
        with open(context_file, "w", encoding="utf-8") as f:
            json.dump(self.contexts[context_key], f, ensure_ascii=False)
            
        return self.contexts[context_key]
    
    def _update_context(self, context_key: str, message: Dict):
        """更新对话上下文"""

        
        if context_key in self.contexts:
            self.contexts[context_key].append(message)
            
            # 保存到localstore
            context_file = os.path.join(self.data_dir, f"{context_key}.json")
            os.makedirs(self.data_dir, exist_ok=True)
            with open(context_file, "w", encoding="utf-8") as f:
                json.dump(self.contexts[context_key], f, ensure_ascii=False)
            

        
    async def handle_stream_output(self, text: str) -> List[str]:
        """处理流式输出"""
        segments = []
        self.stream_buffer += text
        
        # 自动拆分带分段标记的内容
        while "<#br>" in self.stream_buffer:
            index = self.stream_buffer.index("<#br>")
            segments.append(self.stream_buffer[:index])
            self.stream_buffer = self.stream_buffer[index+5:]
            
        return segments
        
    def add_emoji(self, name: str, url: str):
        """添加表情包到库"""
        self.emojis[name] = url
        
    def get_emoji(self, name: str) -> str:
        """获取表情包URL"""
        return self.emojis.get(name, "")
        

        
    def load_emojis_from_dir(self, emoji_dir: str):
        """从指定文件夹加载表情包配置
        :param emoji_dir: 表情包文件夹路径，包含emoji.json和图片文件
        """
        json_path = os.path.join(emoji_dir, "emoji.json")
        
        if not os.path.exists(json_path):
            return
            
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                emoji_config = json.load(f)
                
            for emoji_id, emoji_info in emoji_config.items():
                img_path = os.path.join(emoji_dir, emoji_info["file"])
                if os.path.exists(img_path):
                    self.emojis[emoji_id] = img_path
                    self.emoji_descriptions[emoji_id] = emoji_info.get("description", "")

        except Exception as e:
            print(f"加载表情包配置出错: {str(e)}")

qwen_handler = QwenChatHandler()