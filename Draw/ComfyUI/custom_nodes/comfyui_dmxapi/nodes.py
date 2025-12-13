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
    default_config = {
        "api_key": "",
        "api_url": "https://vip.dmxapi.com/v1/chat/completions",
        "default_model": "gemini-3-pro-image-preview"
    }
    
    # 优先从 Draw/dmxapi_config.json 加载
    # 路径: custom_nodes/comfyui_dmxapi/nodes.py -> ../../.. -> Draw/
    draw_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    config_paths = [
        os.path.join(draw_dir, "dmxapi_config.json"),  # Draw/dmxapi_config.json
        os.path.join(os.path.dirname(__file__), "config.json"),  # 插件目录下的 config.json (备用)
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


# 预设配色方案
COLOR_SCHEMES = {
    "无": "",
    "柔和马卡龙": """【配色方案 - 柔和马卡龙色系】
- 整体风格：淡雅、低饱和度、纯色填充（无渐变无阴影）
- 背景：浅灰白色 (#F5F5F5)
- 根节点：淡天蓝色填充 (#B8D4E8)，深蓝色边框 (#5B9BD5)
- 中间节点：淡杏橙色填充 (#FAE5C8)，橙棕色边框 (#D4A574)
- 叶节点：淡薄荷绿填充 (#C8E6C9)，深绿色边框 (#81C784)
- 连接线：深灰色 (#666666)
- 文字：深灰黑色 (#333333)""",
    "莫兰迪": """【配色方案 - 莫兰迪色系】
- 整体风格：高级灰调、低饱和度、柔和优雅
- 背景：米灰色 (#E8E4E1)
- 主色：灰粉色 (#C9B8B5)、灰蓝色 (#A8B5C4)、灰绿色 (#B5C4B1)
- 强调色：烟灰紫 (#9B8B9E)
- 文字：深灰褐色 (#5C5552)""",
    "赛博朋克": """【配色方案 - 赛博朋克色系】
- 整体风格：高对比度、霓虹感、科技未来
- 背景：深黑色 (#0D0D0D)
- 主色：霓虹粉 (#FF00FF)、电光蓝 (#00FFFF)
- 强调色：荧光绿 (#39FF14)、亮紫 (#BF00FF)
- 文字：白色 (#FFFFFF) 带发光效果""",
    "自然森林": """【配色方案 - 自然森林色系】
- 整体风格：自然、清新、有机感
- 背景：米白色 (#FAF8F5)
- 主色：森林绿 (#228B22)、橄榄绿 (#6B8E23)、苔藓绿 (#8A9A5B)
- 强调色：木棕色 (#8B4513)、土黄色 (#DAA520)
- 文字：深棕色 (#3E2723)""",
    "日式和风": """【配色方案 - 日式和风色系】
- 整体风格：简约、禅意、留白
- 背景：和纸白 (#F5F5DC)
- 主色：墨黑 (#1C1C1C)、朱红 (#C41E3A)、藏青 (#003366)
- 强调色：金色 (#D4AF37)、樱粉 (#FFB7C5)
- 文字：墨黑色 (#1C1C1C)""",
    "商务专业": """【配色方案 - 商务专业色系】
- 整体风格：专业、稳重、清晰
- 背景：纯白色 (#FFFFFF)
- 主色：深蓝 (#003366)、浅蓝 (#4A90D9)
- 强调色：橙色 (#FF6B35)、灰色 (#6C757D)
- 文字：深灰色 (#212529)""",
}

# 边框样式
BORDER_STYLES = {
    "无边框": "【边框样式】无边框，元素之间无明显分隔线",
    "细边框": "【边框样式】细边框（1-2px），简洁清晰",
    "粗边框": "【边框样式】粗边框（3-4px），强调轮廓",
    "圆角边框": "【边框样式】圆角边框，柔和友好",
    "虚线边框": "【边框样式】虚线边框，轻盈活泼",
    "双线边框": "【边框样式】双线边框，正式庄重",
    "阴影边框": "【边框样式】带阴影效果，立体感强",
    "渐变边框": "【边框样式】渐变色边框，现代时尚",
}


class DMXAPIGeminiStyled:
    """
    带颜色风格化的图像生成节点
    可以在生成时指定配色方案
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        # 图像输入
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

    def image_to_base64(self, image_tensor):
        if image_tensor is None:
            return None
        img = image_tensor[0]
        np_img = (img.cpu().numpy() * 255).astype(np.uint8)
        pil_img = Image.fromarray(np_img)
        buffer = io.BytesIO()
        pil_img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def generate(self, prompt, color_scheme, border_style, custom_style,
                 seed=-1, top_p=0.95, **kwargs):
        
        # 动态重新加载配置
        config = load_config()
        url = config.get("api_url", "https://vip.dmxapi.com/v1/chat/completions")
        api_key = config.get("api_key", "")
        model_type = config.get("default_model", "gemini-3-pro-image-preview")
        
        if not api_key:
            print("[DMXAPI] 错误: 未配置 API Key")
            error_img = np.zeros((1, 512, 512, 3), dtype=np.float32)
            error_img[:, :, :, 0] = 1.0
            return (torch.from_numpy(error_img), "错误: 未配置 API Key，请在 Draw/dmxapi_config.json 中设置")
        
        if seed == -1:
            seed = random.randint(0, 2147483647)
        
        content = []
        
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
        
        # 构建完整 prompt
        full_prompt = prompt
        
        # 添加配色方案
        style_text = custom_style if custom_style.strip() else COLOR_SCHEMES.get(color_scheme, "")
        if style_text:
            full_prompt += f"\n\n{style_text}"
        
        # 添加边框样式
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
                
                image_bytes = None
                if resp_content.startswith("/9j/") or resp_content.startswith("iVBOR"):
                    image_bytes = base64.b64decode(resp_content)
                elif "data:image" in resp_content and "base64," in resp_content:
                    import re
                    match = re.search(r'data:image/[^;]+;base64,([A-Za-z0-9+/=]+)', resp_content)
                    if match:
                        image_bytes = base64.b64decode(match.group(1))
                
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
        
        error_img = np.zeros((1, 512, 512, 3), dtype=np.float32)
        error_img[:, :, :, 0] = 1.0
        return (torch.from_numpy(error_img), info_text)


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
        
        # 转换输入图像
        img_tensor = image[0]
        np_img = (img_tensor.cpu().numpy() * 255).astype(np.uint8)
        pil_img = Image.fromarray(np_img)
        buffer = io.BytesIO()
        pil_img.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        
        # 构建风格转换 prompt
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
                
                image_bytes = None
                if resp_content.startswith("/9j/") or resp_content.startswith("iVBOR"):
                    image_bytes = base64.b64decode(resp_content)
                elif "data:image" in resp_content and "base64," in resp_content:
                    import re
                    match = re.search(r'data:image/[^;]+;base64,([A-Za-z0-9+/=]+)', resp_content)
                    if match:
                        image_bytes = base64.b64decode(match.group(1))
                
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


# ==================== 学术插图工作流节点 ====================

# 布局类型
LAYOUT_TYPES = {
    "Linear Pipeline": "左→右流向，适合 Data Processing, Encoding-Decoding",
    "Cyclic/Iterative": "中心包含循环箭头，适合 Optimization, RL, Feedback Loops",
    "Hierarchical Stack": "上→下或下→上堆叠，适合 Multiscale features, Tree structures",
    "Parallel/Dual-Stream": "上下平行的双流结构，适合 Multi-modal fusion, Contrastive Learning",
    "Central Hub": "一个核心模块连接四周组件，适合 Agent-Environment, Knowledge Graphs",
}

ARCHITECT_PROMPT = '''# Role
你是一位 CVPR/NeurIPS 顶刊的**视觉架构师**。你的核心能力是将抽象的论文逻辑转化为**具体的、结构化的、几何级的视觉指令**。

# Objective
阅读我提供的论文内容，输出一份 **[VISUAL SCHEMA]**。这份 Schema 将被直接发送给 AI 绘图模型，因此必须使用**强硬的物理描述**。

# Phase 1: Layout Strategy Selector (布局决策)
请从以下布局原型中选择最合适的一个：
1. **Linear Pipeline**: 左→右流向 (适合 Data Processing, Encoding-Decoding)
2. **Cyclic/Iterative**: 中心包含循环箭头 (适合 Optimization, RL, Feedback Loops)
3. **Hierarchical Stack**: 上→下或下→上堆叠 (适合 Multiscale features, Tree structures)
4. **Parallel/Dual-Stream**: 上下平行的双流结构 (适合 Multi-modal fusion, Contrastive Learning)
5. **Central Hub**: 一个核心模块连接四周组件 (适合 Agent-Environment, Knowledge Graphs)

# Phase 2: Schema Generation Rules
1. **Dynamic Zoning**: 根据选择的布局，定义 2-5 个物理区域 (Zones)
2. **Internal Visualization**: 必须定义每个区域内部的"物体" (Icons, Grids, Trees)，禁止使用抽象概念
3. **Explicit Connections**: 如果是循环过程，必须明确描述 "Curved arrow looping back from Zone X to Zone Y"

# Output Format
请严格遵守以下结构输出：

---BEGIN PROMPT---

[Style & Meta-Instructions]
High-fidelity scientific schematic, technical vector illustration, clean white background, distinct boundaries, academic textbook style. High resolution 4k, strictly 2D flat design.

[LAYOUT CONFIGURATION]
* **Selected Layout**: [布局类型]
* **Composition Logic**: [构图逻辑]
* **Color Palette**: [配色方案]

[ZONE 1: LOCATION - LABEL]
* **Container**: [形状描述]
* **Visual Structure**: [具体描述]
* **Key Text Labels**: "[文本]"

[ZONE 2: LOCATION - LABEL]
...

[CONNECTIONS]
1. [连接线描述]
2. [连接线描述]

---END PROMPT---

# Input Data
'''

RENDERER_PROMPT = '''**Style Reference & Execution Instructions:**

1. **Art Style (Visio/Illustrator Aesthetic):**
   Generate a **professional academic architecture diagram** suitable for a top-tier computer science paper (CVPR/NeurIPS).
   * **Visuals:** Flat vector graphics, distinct geometric shapes, clean thin outlines, and soft pastel fills.
   * **Layout:** Strictly follow the spatial arrangement defined below.
   * **Vibe:** Technical, precise, clean white background. NOT hand-drawn, NOT photorealistic, NOT 3D render, NO shadows/shading.

2. **CRITICAL TEXT CONSTRAINTS:**
   * **DO NOT render meta-labels:** Do not write words like "ZONE 1", "LAYOUT CONFIGURATION", "Input", "Output", or "Container" inside the image.
   * **ONLY render "Key Text Labels":** Only text inside double quotes listed under "Key Text Labels" should appear in the diagram.
   * **Font:** Use a clean, bold Sans-Serif font for all labels.

3. **Visual Schema Execution:**
   Translate the following structural blueprint into the final image:

'''


class AcademicArchitect:
    """
    Step 1: The Architect - 将论文内容转化为 Visual Schema
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "paper_content": ("STRING", {
                    "multiline": True,
                    "default": "在此粘贴论文摘要或方法章节内容..."
                }),
                "layout_hint": (list(LAYOUT_TYPES.keys()), {"default": "Linear Pipeline"}),
                "zone_count": ("INT", {"default": 3, "min": 2, "max": 5}),
            },
            "optional": {
                "custom_instructions": ("STRING", {
                    "multiline": True,
                    "default": ""
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("visual_schema", "full_prompt")
    FUNCTION = "generate_schema"
    CATEGORY = "DMXAPI/Academic"

    def generate_schema(self, paper_content, layout_hint, zone_count, custom_instructions=""):
        config = load_config()
        api_key = config.get("api_key", "")
        url = config.get("api_url", "https://vip.dmxapi.com/v1/chat/completions")
        
        if not api_key:
            return ("错误: 未配置 API Key", "")
        
        # 构建 Architect Prompt
        full_prompt = ARCHITECT_PROMPT + paper_content
        if custom_instructions:
            full_prompt += f"\n\n# Additional Instructions\n{custom_instructions}"
        full_prompt += f"\n\n# Hints\n- 建议使用 {layout_hint} 布局\n- 建议划分 {zone_count} 个区域"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        
        payload = {
            "model": "gemini-3-pro-preview",  # 使用推理能力强的模型
            "messages": [{"role": "user", "content": full_prompt}],
            "temperature": 0.7,
        }
        
        try:
            print("[Architect] 正在生成 Visual Schema...")
            response = requests.post(url, headers=headers, json=payload, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                schema = result["choices"][0]["message"]["content"]
                print("[Architect] Schema 生成成功")
                return (schema, full_prompt)
            else:
                error = f"API 错误: {response.status_code}"
                print(f"[Architect] {error}")
                return (error, full_prompt)
                
        except Exception as e:
            error = f"错误: {str(e)}"
            print(f"[Architect] {error}")
            return (error, full_prompt)


class AcademicRenderer:
    """
    Step 2: The Renderer - 将 Visual Schema 渲染为图像
    支持多张参考图片输入
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        # 生成多个图像输入槽
        image_inputs = {f"ref_image_{i}": ("IMAGE",) for i in range(1, 9)}
        
        return {
            "required": {
                "visual_schema": ("STRING", {
                    "multiline": True,
                    "default": "粘贴 Architect 生成的 Visual Schema 或直接输入绘图描述..."
                }),
                "color_palette": ("STRING", {
                    "default": "Azure Blue (#E1F5FE), Slate Grey (#607D8B), Coral Orange (#FF7043), Mint Green (#A5D6A7)"
                }),
            },
            "optional": image_inputs
        }
    
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "info")
    FUNCTION = "render"
    CATEGORY = "DMXAPI/Academic"

    def image_to_base64(self, image_tensor, max_size=800):
        """将图像张量转换为 base64，自动压缩大图"""
        if image_tensor is None:
            return None
        img = image_tensor[0]
        np_img = (img.cpu().numpy() * 255).astype(np.uint8)
        pil_img = Image.fromarray(np_img)
        
        # 压缩大图
        w, h = pil_img.size
        if w > max_size or h > max_size:
            ratio = min(max_size / w, max_size / h)
            new_size = (int(w * ratio), int(h * ratio))
            pil_img = pil_img.resize(new_size, Image.LANCZOS)
            print(f"[Renderer] 压缩参考图: {w}x{h} -> {new_size[0]}x{new_size[1]}")
        
        buffer = io.BytesIO()
        pil_img.save(buffer, format="JPEG", quality=85)  # 用 JPEG 减小体积
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def render(self, visual_schema, color_palette="", **kwargs):
        config = load_config()
        api_key = config.get("api_key", "")
        url = config.get("api_url", "https://vip.dmxapi.com/v1/chat/completions")
        model_type = config.get("default_model", "gemini-3-pro-image-preview")
        
        if not api_key:
            error_img = np.zeros((1, 512, 512, 3), dtype=np.float32)
            error_img[:, :, :, 0] = 1.0
            return (torch.from_numpy(error_img), "错误: 未配置 API Key")
        
        # 提取 Schema 中的核心内容
        schema_content = visual_schema
        if "---BEGIN PROMPT---" in visual_schema and "---END PROMPT---" in visual_schema:
            start = visual_schema.find("---BEGIN PROMPT---") + len("---BEGIN PROMPT---")
            end = visual_schema.find("---END PROMPT---")
            schema_content = visual_schema[start:end].strip()
        
        # 限制 schema 长度，避免 prompt 过长
        max_schema_len = 4000
        if len(schema_content) > max_schema_len:
            print(f"[Renderer] Schema 过长 ({len(schema_content)} chars)，截断至 {max_schema_len}")
            schema_content = schema_content[:max_schema_len] + "\n...(truncated)"
        
        # 构建简化的渲染 Prompt
        render_prompt = f"""Generate a professional academic diagram based on this description:

{schema_content}

Style requirements:
- Flat vector graphics, clean lines
- Professional academic paper style
- Clean white background
- No 3D effects or shadows"""
        
        if color_palette:
            render_prompt += f"\n- Colors: {color_palette}"
        
        content = []
        
        # 收集参考图像（最多 2 张，避免请求过大）
        max_ref_images = 2
        ref_count = 0
        for i in range(1, 9):
            if ref_count >= max_ref_images:
                break
            ref_img = kwargs.get(f"ref_image_{i}")
            if ref_img is not None:
                img_base64 = self.image_to_base64(ref_img)
                if img_base64:
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}
                    })
                    ref_count += 1
        
        if ref_count > 0:
            render_prompt += f"\n- Match the visual style of the {ref_count} reference image(s)"
        
        content.append({
            "type": "text",
            "text": render_prompt
        })
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        
        payload = {
            "model": model_type,
            "messages": [{"role": "user", "content": content}],
        }
        
        info_text = "Renderer 执行中..."
        
        print(f"[Renderer] Prompt 长度: {len(render_prompt)} chars, 参考图: {ref_count}")
        
        try:
            print("[Renderer] 正在渲染图像...")
            response = requests.post(url, headers=headers, json=payload, timeout=180)
            
            if response.status_code == 200:
                result = response.json()
                resp_content = result["choices"][0]["message"]["content"]
                
                image_bytes = None
                if resp_content.startswith("/9j/") or resp_content.startswith("iVBOR"):
                    image_bytes = base64.b64decode(resp_content)
                elif "data:image" in resp_content and "base64," in resp_content:
                    import re
                    match = re.search(r'data:image/[^;]+;base64,([A-Za-z0-9+/=]+)', resp_content)
                    if match:
                        image_bytes = base64.b64decode(match.group(1))
                
                if image_bytes:
                    pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                    np_image = np.array(pil_image).astype(np.float32) / 255.0
                    info_text = f"渲染成功: {pil_image.size}"
                    print(f"[Renderer] {info_text}")
                    return (torch.from_numpy(np_image).unsqueeze(0), info_text)
                else:
                    info_text = f"返回文本: {resp_content[:200]}"
            else:
                error_detail = response.text[:500] if response.text else "无详细信息"
                info_text = f"API 错误: {response.status_code} - {error_detail}"
                print(f"[Renderer] {info_text}")
                
        except Exception as e:
            info_text = f"错误: {str(e)}"
        
        print(f"[Renderer] {info_text}")
        error_img = np.zeros((1, 512, 512, 3), dtype=np.float32)
        error_img[:, :, :, 0] = 1.0
        return (torch.from_numpy(error_img), info_text)


class AcademicEditor:
    """
    Step 3: The Editor - 对生成的图像进行自然语言编辑
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "edit_instruction": ("STRING", {
                    "multiline": True,
                    "default": "例如: Make all lines thinner, change the orange arrows to dark grey"
                }),
            },
        }
    
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "info")
    FUNCTION = "edit"
    CATEGORY = "DMXAPI/Academic"

    def edit(self, image, edit_instruction):
        config = load_config()
        api_key = config.get("api_key", "")
        url = config.get("api_url", "https://vip.dmxapi.com/v1/chat/completions")
        model_type = config.get("default_model", "gemini-3-pro-image-preview")
        
        if not api_key:
            return (image, "错误: 未配置 API Key")
        
        # 转换图像
        img_tensor = image[0]
        np_img = (img_tensor.cpu().numpy() * 255).astype(np.uint8)
        pil_img = Image.fromarray(np_img)
        buffer = io.BytesIO()
        pil_img.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        
        edit_prompt = f"""You are editing an academic diagram. Please make the following modifications while preserving the overall structure and layout:

{edit_instruction}

Important:
- Keep the diagram style professional and suitable for academic papers
- Maintain clean lines and flat 2D design
- Do not add shadows or 3D effects
- Preserve all existing text labels unless specifically asked to change them"""
        
        content = [
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_base64}"}},
            {"type": "text", "text": edit_prompt}
        ]
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        
        payload = {
            "model": model_type,
            "messages": [{"role": "user", "content": content}],
        }
        
        info_text = "Editor 执行中..."
        
        try:
            print(f"[Editor] 正在编辑: {edit_instruction[:50]}...")
            response = requests.post(url, headers=headers, json=payload, timeout=180)
            
            if response.status_code == 200:
                result = response.json()
                resp_content = result["choices"][0]["message"]["content"]
                
                image_bytes = None
                if resp_content.startswith("/9j/") or resp_content.startswith("iVBOR"):
                    image_bytes = base64.b64decode(resp_content)
                elif "data:image" in resp_content and "base64," in resp_content:
                    import re
                    match = re.search(r'data:image/[^;]+;base64,([A-Za-z0-9+/=]+)', resp_content)
                    if match:
                        image_bytes = base64.b64decode(match.group(1))
                
                if image_bytes:
                    pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                    np_image = np.array(pil_image).astype(np.float32) / 255.0
                    info_text = f"编辑成功: {pil_image.size}"
                    print(f"[Editor] {info_text}")
                    return (torch.from_numpy(np_image).unsqueeze(0), info_text)
                else:
                    info_text = f"返回文本: {resp_content[:100]}"
            else:
                info_text = f"API 错误: {response.status_code}"
                
        except Exception as e:
            info_text = f"错误: {str(e)}"
        
        print(f"[Editor] {info_text}")
        return (image, info_text)


# 节点注册
NODE_CLASS_MAPPINGS = {
    "DMXAPIGeminiImageGen": DMXAPIGeminiImageGen,
    "DMXAPIGeminiImageEdit": DMXAPIGeminiImageEdit,
    "DMXAPIGeminiMultiImage": DMXAPIGeminiMultiImage,
    "DMXAPIGeminiImageBatch": DMXAPIGeminiImageBatch,
    "DMXAPIGeminiStyled": DMXAPIGeminiStyled,
    "DMXAPIStyleTransfer": DMXAPIStyleTransfer,
    "AcademicArchitect": AcademicArchitect,
    "AcademicRenderer": AcademicRenderer,
    "AcademicEditor": AcademicEditor,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DMXAPIGeminiImageGen": "DMXAPI Gemini 图像生成",
    "DMXAPIGeminiImageEdit": "DMXAPI Gemini 图像编辑",
    "DMXAPIGeminiMultiImage": "DMXAPI Gemini 多图生成",
    "DMXAPIGeminiImageBatch": "DMXAPI Gemini 批量图像",
    "DMXAPIGeminiStyled": "DMXAPI Gemini 风格化生成",
    "DMXAPIStyleTransfer": "DMXAPI 风格转换",
    "AcademicArchitect": "学术插图 - 逻辑构建 (Architect)",
    "AcademicRenderer": "学术插图 - 视觉渲染 (Renderer)",
    "AcademicEditor": "学术插图 - 交互编辑 (Editor)",
}
