from pydantic import BaseModel, Field, Extra
from nonebot import get_plugin_config

class Config(BaseModel, extra=Extra.ignore):
    qwen_api_key: str = Field(default="", description="阿里云通义千问API密钥")
    qwen_model: str = Field(default="qwen-turbo", description="使用的模型名称")

    name: str = Field(default="", description="机器人名称")
    max_tokens: int = Field(default=1500, description="最大token数")
    temperature: float = Field(default=0.9, description="温度参数")
    emoji_dir: str = Field(default="", description="表情包目录路径")
    role: str = Field(default="", description="机器人角色设定")
    
    def is_qwen_model(self):
        return self.qwen_model.startswith("qwen")
        
    def is_vl_model(self):
        return self.qwen_model.startswith("qwen-vl")
        
    def is_omni_model(self):
        return self.qwen_model.startswith("qwen-omni")