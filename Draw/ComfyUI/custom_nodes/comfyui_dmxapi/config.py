"""
配置加载模块
"""

import os
import json


def load_config():
    """加载配置文件"""
    default_config = {
        "api_key": "",
        "api_url": "https://vip.dmxapi.com/v1/chat/completions",
        "text_model": "gemini-2.5-pro-preview-06-05",
        "image_model": "gemini-2.5-flash-preview-05-20"
    }
    
    # 优先从 Draw/config_llm.json 加载
    # 路径: custom_nodes/comfyui_dmxapi/ -> ../../.. -> Draw/
    draw_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    config_paths = [
        os.path.join(draw_dir, "config_llm.json"),
    ]
    
    for config_path in config_paths:
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = {**default_config, **json.load(f)}
                    print(f"[DMXAPI] 已加载配置: {config_path}")
                    return config
            except Exception as e:
                print(f"[DMXAPI] 加载配置失败 ({config_path}): {e}")
    
    print("[DMXAPI] 未找到配置文件，使用默认配置")
    return default_config


# 全局配置实例
CONFIG = load_config()
