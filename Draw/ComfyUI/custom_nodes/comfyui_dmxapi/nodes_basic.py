"""
基础图像生成/编辑节点
"""

import requests
import numpy as np
import torch
from PIL import Image
import io
import random

from .config import CONFIG, load_config
from .utils import image_to_base64, parse_image_from_response, bytes_to_tensor, create_error_image


class DMXAPIGeminiImageGen:
    """使用 DMXAPI 的 Gemini 模型生成图像"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "一只可爱的橘猫在阳光下睡觉"
                }),
                "api_key": ("STRING", {
                    "default": CONFIG.get("api_key", "")
                }),
            },
            "optional": {
                "temperature": ("FLOAT", {
                    "default": 0.7,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.1
                }),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "generate"
    CATEGORY = "DMXAPI"

    def generate(self, prompt, api_key, temperature=0.7):
        url = CONFIG.get("api_url", "https://vip.dmxapi.com/v1/chat/completions")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "DMXAPI/1.0.0 (https://www.dmxapi.com/)",
        }

        payload = {
            "model": "gemini-3-pro-image-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}],
                },
            ],
            "temperature": temperature,
            "user": "DMXAPI",
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                image_bytes = parse_image_from_response(content)
                if image_bytes:
                    return (bytes_to_tensor(image_bytes),)
                else:
                    raise ValueError(f"未识别的图像格式: {content[:50]}...")
            else:
                raise ValueError(f"API 请求失败: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"[DMXAPI] 错误: {e}")
            return (create_error_image(),)


class DMXAPIGeminiImageEdit:
    """使用 DMXAPI 的 Gemini 模型编辑图像"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "把背景改成海边"
                }),
                "api_key": ("STRING", {
                    "default": CONFIG.get("api_key", "")
                }),
            },
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "edit"
    CATEGORY = "DMXAPI"

    def edit(self, image, prompt, api_key):
        url = CONFIG.get("api_url", "https://vip.dmxapi.com/v1/chat/completions")
        
        img_base64 = image_to_base64(image)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "DMXAPI/1.0.0 (https://www.dmxapi.com/)",
        }
        
        payload = {
            "model": "gemini-3-pro-image-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{img_base64}"}
                        },
                        {"type": "text", "text": prompt}
                    ],
                },
            ],
            "user": "DMXAPI",
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                image_bytes = parse_image_from_response(content)
                if image_bytes:
                    return (bytes_to_tensor(image_bytes),)
                else:
                    print(f"[DMXAPI] 返回文本: {content[:200]}")
                    return (image,)
            else:
                raise ValueError(f"API 请求失败: {response.status_code}")
                
        except Exception as e:
            print(f"[DMXAPI] 错误: {e}")
            return (image,)


class DMXAPIGeminiMultiImage:
    """
    多图输入的 Gemini 图像生成节点
    支持最多 16 张图片输入
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        optional_inputs = {}
        for i in range(1, 17):
            optional_inputs[f"image_{i}"] = ("IMAGE",)
        
        optional_inputs.update({
            "batch_size": ("INT", {"default": 1, "min": 1, "max": 4}),
            "aspect_ratio": (["Auto", "1:1", "16:9", "9:16", "4:3", "3:4"], {"default": "Auto"}),
            "seed": ("INT", {"default": -1, "min": -1, "max": 2147483647}),
            "randomize": ("BOOLEAN", {"default": True}),
            "top_p": ("FLOAT", {"default": 0.95, "min": 0.0, "max": 1.0, "step": 0.05}),
            "image_size": (["1K", "2K", "4K"], {"default": "2K"}),
        })
        
        return {
            "required": {
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "根据输入的图片生成新图像，保持人物特征不变"
                }),
                "api_key": ("STRING", {
                    "default": CONFIG.get("api_key", "")
                }),
                "model_type": ("STRING", {
                    "default": CONFIG.get("default_model", "gemini-3-pro-image-preview")
                }),
            },
            "optional": optional_inputs
        }
    
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("images", "info")
    FUNCTION = "generate"
    CATEGORY = "DMXAPI"

    def generate(self, prompt, api_key, model_type, 
                 batch_size=1, aspect_ratio="Auto", seed=-1, randomize=True, 
                 top_p=0.95, image_size="2K", **kwargs):
        
        url = CONFIG.get("api_url", "https://vip.dmxapi.com/v1/chat/completions")
        
        if randomize or seed == -1:
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
        if aspect_ratio != "Auto":
            full_prompt += f"\n图像比例: {aspect_ratio}"
        if image_size == "4K":
            full_prompt += "\n生成高分辨率4K图像"
        elif image_size == "1K":
            full_prompt += "\n生成1K分辨率图像"
            
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

        all_images = []
        info_text = f"Seed: {seed}\nImages: {img_count}\nModel: {model_type}"
        
        print(f"[DMXAPI] 开始请求，输入图像数: {img_count}, prompt: {prompt[:50]}...")
        
        try:
            for i in range(batch_size):
                print(f"[DMXAPI] 发送请求 {i+1}/{batch_size}...")
                response = requests.post(url, headers=headers, json=payload, timeout=180)
                
                print(f"[DMXAPI] 响应状态码: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    resp_content = result["choices"][0]["message"]["content"]
                    
                    print(f"[DMXAPI] 响应内容前100字符: {resp_content[:100]}")
                    
                    image_bytes = parse_image_from_response(resp_content)
                    if image_bytes:
                        pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                        np_image = np.array(pil_image).astype(np.float32) / 255.0
                        all_images.append(np_image)
                        info_text += f"\n[{i+1}] 生成成功: {pil_image.size}"
                        print(f"[DMXAPI] 图像生成成功: {pil_image.size}")
                    else:
                        info_text += f"\n[{i+1}] 返回文本: {resp_content[:100]}"
                        print(f"[DMXAPI] 返回的是文本，不是图像")
                else:
                    error_detail = response.text[:200]
                    info_text += f"\n[{i+1}] 失败: {response.status_code} - {error_detail}"
                    print(f"[DMXAPI] 请求失败: {response.status_code} - {error_detail}")
            
            if all_images:
                stacked = np.stack(all_images, axis=0)
                return (torch.from_numpy(stacked), info_text)
            else:
                return (create_error_image(), info_text)
                
        except Exception as e:
            error_msg = f"错误: {str(e)}"
            print(f"[DMXAPI] {error_msg}")
            return (create_error_image(), error_msg)


class DMXAPIGeminiImageBatch:
    """
    接收批量图像输入的节点
    可以接收 batch 图像（多张图堆叠在一起）
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "根据这些图片生成新图像"
                }),
                "api_key": ("STRING", {
                    "default": CONFIG.get("api_key", "")
                }),
            },
            "optional": {
                "model_type": ("STRING", {"default": CONFIG.get("default_model", "gemini-3-pro-image-preview")}),
                "max_images": ("INT", {"default": 5, "min": 1, "max": 10}),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "info")
    FUNCTION = "generate"
    CATEGORY = "DMXAPI"

    def generate(self, images, prompt, api_key, model_type=None, max_images=5):
        if model_type is None:
            model_type = CONFIG.get("default_model", "gemini-3-pro-image-preview")
        url = CONFIG.get("api_url", "https://vip.dmxapi.com/v1/chat/completions")
        
        batch_size = images.shape[0]
        num_images = min(batch_size, max_images)
        
        content = []
        
        for i in range(num_images):
            img_base64 = image_to_base64(images[i:i+1])
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{img_base64}"}
            })
        
        content.append({"type": "text", "text": prompt})
        
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
        
        info_text = f"输入图像数: {num_images}"

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=180)
            
            if response.status_code == 200:
                result = response.json()
                resp_content = result["choices"][0]["message"]["content"]
                
                image_bytes = parse_image_from_response(resp_content)
                if image_bytes:
                    pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                    info_text += f"\n生成成功: {pil_image.size}"
                    return (bytes_to_tensor(image_bytes), info_text)
                else:
                    info_text += f"\n返回文本: {resp_content[:200]}"
                    return (images[:1], info_text)
            else:
                info_text += f"\n失败: {response.status_code} - {response.text[:100]}"
                return (images[:1], info_text)
                
        except Exception as e:
            error_msg = f"错误: {str(e)}"
            print(f"[DMXAPI] {error_msg}")
            return (images[:1], error_msg)
