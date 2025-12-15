"""
风格化图像生成节点
"""

import requests
import numpy as np
import torch
from PIL import Image
import io
import base64
import random

from .config import CONFIG, load_config
from .constants import COLOR_SCHEMES, BORDER_STYLES
from .utils import image_to_base64, parse_image_from_response, bytes_to_tensor, create_error_image


class DMXAPIGeminiStyled:
    """
    带颜色风格化的图像生成节点
    可以在生成时指定配色方案
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        image_inputs = {f"image_{i}": ("IMAGE",) for i in range(1, 17)}
        
        return {
            "required": {
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "生成一张图像"
                }),
                "color_scheme": (list(COLOR_SCHEMES.keys()), {"default": "无"}),
                "border_style": (list(BORDER_STYLES.keys()), {"default": "无边框"}),
                "custom_style": ("STRING", {
                    "multiline": True,
                    "default": ""
                }),
                "seed": ("INT", {"default": -1, "min": -1, "max": 2147483647}),
                "top_p": ("FLOAT", {"default": 0.95, "min": 0.0, "max": 1.0, "step": 0.05}),
            },
            "optional": image_inputs
        }
    
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "info")
    FUNCTION = "generate"
    CATEGORY = "DMXAPI"

    def generate(self, prompt, color_scheme, border_style, custom_style,
                 seed=-1, top_p=0.95, **kwargs):
        
        config = load_config()
        url = config.get("api_url", "https://vip.dmxapi.com/v1/chat/completions")
        api_key = config.get("api_key", "")
        model_type = config.get("default_model", "gemini-3-pro-image-preview")
        
        if not api_key:
            print("[DMXAPI] 错误: 未配置 API Key")
            return (create_error_image(), "错误: 未配置 API Key，请在 Draw/config_llm.json 中设置")
        
        if seed == -1:
            seed = random.randint(0, 2147483647)
        
        content = []
        
        img_count = 0
        for i in range(1, 17):
            img = kwargs.get(f"image_{i}")
            if img is not None:
                img_base64 = image_to_base64(img)
                if img_base64:
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{img_base64}"}
                    })
                    img_count += 1
        
        full_prompt = prompt
        
        style_text = custom_style if custom_style.strip() else COLOR_SCHEMES.get(color_scheme, "")
        if style_text:
            full_prompt += f"\n\n{style_text}"
        
        border_text = BORDER_STYLES.get(border_style, "")
        if border_text and border_style != "无边框":
            full_prompt += f"\n\n{border_text}"
        
        content.append({"type": "text", "text": full_prompt})
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "DMXAPI/1.0.0 (https://www.dmxapi.com/)",
        }
        
        payload = {
            "model": model_type,
            "messages": [{"role": "user", "content": content}],
            "top_p": top_p,
            "user": "DMXAPI",
        }

        info_text = f"Seed: {seed}\nImages: {img_count}\nStyle: {color_scheme}"
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=180)
            
            if response.status_code == 200:
                result = response.json()
                resp_content = result["choices"][0]["message"]["content"]
                
                image_bytes = parse_image_from_response(resp_content)
                if image_bytes:
                    pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                    np_image = np.array(pil_image).astype(np.float32) / 255.0
                    info_text += f"\n生成成功: {pil_image.size}"
                    return (torch.from_numpy(np_image).unsqueeze(0), info_text)
                else:
                    info_text += f"\n返回文本: {resp_content[:100]}"
            else:
                info_text += f"\n失败: {response.status_code}"
                
        except Exception as e:
            info_text += f"\n错误: {str(e)}"
        
        return (create_error_image(), info_text)


class DMXAPIStyleTransfer:
    """
    图像风格转换节点
    对已有图像应用配色方案
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "color_scheme": (list(COLOR_SCHEMES.keys()), {"default": "柔和马卡龙"}),
                "custom_style": ("STRING", {
                    "multiline": True,
                    "default": ""
                }),
                "api_key": ("STRING", {
                    "default": CONFIG.get("api_key", "")
                }),
            },
            "optional": {
                "additional_prompt": ("STRING", {
                    "multiline": True,
                    "default": ""
                }),
                "model_type": ("STRING", {"default": CONFIG.get("default_model", "gemini-3-pro-image-preview")}),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "info")
    FUNCTION = "transfer"
    CATEGORY = "DMXAPI"

    def transfer(self, image, color_scheme, custom_style, api_key, 
                 additional_prompt="", model_type=None):
        if model_type is None:
            model_type = CONFIG.get("default_model", "gemini-3-pro-image-preview")
        url = CONFIG.get("api_url", "https://vip.dmxapi.com/v1/chat/completions")
        
        img_base64 = image_to_base64(image)
        
        style_text = custom_style if custom_style.strip() else COLOR_SCHEMES.get(color_scheme, "")
        prompt = f"请将这张图片按照以下配色方案重新生成，保持原有内容和布局不变：\n\n{style_text}"
        if additional_prompt:
            prompt += f"\n\n额外要求：{additional_prompt}"
        
        content = [
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_base64}"}},
            {"type": "text", "text": prompt}
        ]
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "DMXAPI/1.0.0 (https://www.dmxapi.com/)",
        }
        
        payload = {
            "model": model_type,
            "messages": [{"role": "user", "content": content}],
            "user": "DMXAPI",
        }
        
        info_text = f"Style: {color_scheme}"

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=180)
            
            if response.status_code == 200:
                result = response.json()
                resp_content = result["choices"][0]["message"]["content"]
                
                image_bytes = parse_image_from_response(resp_content)
                if image_bytes:
                    pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                    np_image = np.array(pil_image).astype(np.float32) / 255.0
                    info_text += f"\n转换成功: {pil_image.size}"
                    return (torch.from_numpy(np_image).unsqueeze(0), info_text)
                else:
                    info_text += f"\n返回文本: {resp_content[:100]}"
            else:
                info_text += f"\n失败: {response.status_code}"
                
        except Exception as e:
            info_text += f"\n错误: {str(e)}"
        
        return (image, info_text)
