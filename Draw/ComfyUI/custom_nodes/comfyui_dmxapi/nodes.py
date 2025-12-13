"""
ComfyUI 自定义节点 - DMXAPI Gemini 图像生成
调用 dmxapi 的 gemini-3-pro-image-preview 模型生成图像
"""

import requests
import base64
import numpy as np
import torch
from PIL import Image
import io
import random
import json
import os

# 加载配置文件
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    default_config = {
        "api_key": "",
        "api_url": "https://vip.dmxapi.com/v1/chat/completions",
        "default_model": "gemini-3-pro-image-preview"
    }
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return {**default_config, **json.load(f)}
        except Exception as e:
            print(f"[DMXAPI] 加载配置失败: {e}")
    return default_config

CONFIG = load_config()


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
                
                # 解析 base64 图像
                import re
                image_bytes = None
                
                if content.startswith("/9j/") or content.startswith("iVBOR"):
                    image_bytes = base64.b64decode(content)
                elif "data:image" in content and "base64," in content:
                    match = re.search(r'data:image/[^;]+;base64,([A-Za-z0-9+/=]+)', content)
                    if match:
                        image_bytes = base64.b64decode(match.group(1))
                
                if not image_bytes:
                    raise ValueError(f"未识别的图像格式: {content[:50]}...")
                
                # 转换为 PIL Image
                pil_image = Image.open(io.BytesIO(image_bytes))
                pil_image = pil_image.convert("RGB")
                
                # 转换为 ComfyUI 格式 (B, H, W, C) float32 [0,1]
                np_image = np.array(pil_image).astype(np.float32) / 255.0
                tensor_image = torch.from_numpy(np_image).unsqueeze(0)
                
                return (tensor_image,)
            else:
                raise ValueError(f"API 请求失败: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"[DMXAPI] 错误: {e}")
            # 返回一个红色错误图像
            error_img = np.zeros((512, 512, 3), dtype=np.float32)
            error_img[:, :, 0] = 1.0  # 红色
            return (torch.from_numpy(error_img).unsqueeze(0),)


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
        
        # 将输入图像转换为 base64
        img_tensor = image[0]  # (H, W, C)
        np_img = (img_tensor.cpu().numpy() * 255).astype(np.uint8)
        pil_img = Image.fromarray(np_img)
        
        buffer = io.BytesIO()
        pil_img.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        
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
                
                import re
                image_bytes = None
                
                if content.startswith("/9j/") or content.startswith("iVBOR"):
                    image_bytes = base64.b64decode(content)
                elif "data:image" in content and "base64," in content:
                    match = re.search(r'data:image/[^;]+;base64,([A-Za-z0-9+/=]+)', content)
                    if match:
                        image_bytes = base64.b64decode(match.group(1))
                
                if image_bytes:
                    pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                    np_image = np.array(pil_image).astype(np.float32) / 255.0
                    return (torch.from_numpy(np_image).unsqueeze(0),)
                else:
                    print(f"[DMXAPI] 返回文本: {content[:200]}")
                    return (image,)  # 返回原图
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
        # 生成 16 个图像输入槽
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

    def image_to_base64(self, image_tensor):
        """将 ComfyUI 图像张量转换为 base64"""
        if image_tensor is None:
            return None
        img = image_tensor[0]  # (H, W, C)
        np_img = (img.cpu().numpy() * 255).astype(np.uint8)
        pil_img = Image.fromarray(np_img)
        buffer = io.BytesIO()
        pil_img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def generate(self, prompt, api_key, model_type, 
                 batch_size=1, aspect_ratio="Auto", seed=-1, randomize=True, 
                 top_p=0.95, image_size="2K", **kwargs):
        
        url = CONFIG.get("api_url", "https://vip.dmxapi.com/v1/chat/completions")
        
        # 处理 seed
        if randomize or seed == -1:
            seed = random.randint(0, 2147483647)
        
        # 构建消息内容
        content = []
        
        # 从 kwargs 中提取所有 image_N 参数（支持 16 张图）
        img_count = 0
        for i in range(1, 17):
            img = kwargs.get(f"image_{i}")
            if img is not None:
                img_base64 = self.image_to_base64(img)
                if img_base64:
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{img_base64}"}
                    })
                    img_count += 1
        
        # 添加提示词
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
                    
                    # 尝试从响应中提取 base64 图像
                    image_bytes = None
                    
                    # 情况1: 直接是 base64 字符串
                    if resp_content.startswith("/9j/") or resp_content.startswith("iVBOR"):
                        image_bytes = base64.b64decode(resp_content)
                    # 情况2: Markdown 格式 ![image](data:image/...;base64,...)
                    elif "data:image" in resp_content and "base64," in resp_content:
                        import re
                        match = re.search(r'data:image/[^;]+;base64,([A-Za-z0-9+/=]+)', resp_content)
                        if match:
                            image_bytes = base64.b64decode(match.group(1))
                            print(f"[DMXAPI] 从 Markdown 格式提取图像成功")
                    
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
                # 堆叠所有图像
                stacked = np.stack(all_images, axis=0)
                return (torch.from_numpy(stacked), info_text)
            else:
                # 返回错误图像
                error_img = np.zeros((1, 512, 512, 3), dtype=np.float32)
                error_img[:, :, :, 0] = 1.0
                return (torch.from_numpy(error_img), info_text)
                
        except Exception as e:
            error_msg = f"错误: {str(e)}"
            print(f"[DMXAPI] {error_msg}")
            error_img = np.zeros((1, 512, 512, 3), dtype=np.float32)
            error_img[:, :, :, 0] = 1.0
            return (torch.from_numpy(error_img), error_msg)


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
        
        # images 是 (B, H, W, C) 格式，B 是 batch size
        batch_size = images.shape[0]
        num_images = min(batch_size, max_images)
        
        content = []
        
        # 添加所有图像
        for i in range(num_images):
            img_tensor = images[i]  # (H, W, C)
            np_img = (img_tensor.cpu().numpy() * 255).astype(np.uint8)
            pil_img = Image.fromarray(np_img)
            buffer = io.BytesIO()
            pil_img.save(buffer, format="PNG")
            img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
            
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
                
                if resp_content.startswith("/9j/") or resp_content.startswith("iVBOR"):
                    image_bytes = base64.b64decode(resp_content)
                    pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                    np_image = np.array(pil_image).astype(np.float32) / 255.0
                    info_text += f"\n生成成功: {pil_image.size}"
                    return (torch.from_numpy(np_image).unsqueeze(0), info_text)
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


# 节点注册
NODE_CLASS_MAPPINGS = {
    "DMXAPIGeminiImageGen": DMXAPIGeminiImageGen,
    "DMXAPIGeminiImageEdit": DMXAPIGeminiImageEdit,
    "DMXAPIGeminiMultiImage": DMXAPIGeminiMultiImage,
    "DMXAPIGeminiImageBatch": DMXAPIGeminiImageBatch,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DMXAPIGeminiImageGen": "DMXAPI Gemini 图像生成",
    "DMXAPIGeminiImageEdit": "DMXAPI Gemini 图像编辑",
    "DMXAPIGeminiMultiImage": "DMXAPI Gemini 多图生成",
    "DMXAPIGeminiImageBatch": "DMXAPI Gemini 批量图像",
}
