"""
公共工具函数模块
"""

import base64
import io
import re
import numpy as np
import torch
from PIL import Image


def image_to_base64(image_tensor, format="PNG", max_size=None, quality=95):
    """
    将 ComfyUI 图像张量转换为 base64
    
    Args:
        image_tensor: ComfyUI 图像张量 (B, H, W, C)
        format: 图像格式 ("PNG" 或 "JPEG")
        max_size: 最大尺寸，超过则压缩
        quality: JPEG 质量 (1-100)
    
    Returns:
        base64 编码的字符串，或 None
    """
    if image_tensor is None:
        return None
    
    img = image_tensor[0]  # (H, W, C)
    np_img = (img.cpu().numpy() * 255).astype(np.uint8)
    pil_img = Image.fromarray(np_img)
    
    # 压缩大图
    if max_size:
        w, h = pil_img.size
        if w > max_size or h > max_size:
            ratio = min(max_size / w, max_size / h)
            new_size = (int(w * ratio), int(h * ratio))
            pil_img = pil_img.resize(new_size, Image.LANCZOS)
    
    buffer = io.BytesIO()
    if format.upper() == "JPEG":
        pil_img.save(buffer, format="JPEG", quality=quality)
    else:
        pil_img.save(buffer, format="PNG")
    
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def parse_image_from_response(content):
    """
    从 API 响应中解析 base64 图像
    
    Args:
        content: API 响应内容字符串
    
    Returns:
        图像字节数据，或 None
    """
    # 情况1: 直接是 base64 字符串
    if content.startswith("/9j/") or content.startswith("iVBOR"):
        return base64.b64decode(content)
    
    # 情况2: Markdown 格式 ![image](data:image/...;base64,...)
    if "data:image" in content and "base64," in content:
        match = re.search(r'data:image/[^;]+;base64,([A-Za-z0-9+/=]+)', content)
        if match:
            return base64.b64decode(match.group(1))
    
    return None


def bytes_to_tensor(image_bytes):
    """
    将图像字节数据转换为 ComfyUI 张量
    
    Args:
        image_bytes: 图像字节数据
    
    Returns:
        ComfyUI 格式的图像张量 (1, H, W, C)
    """
    pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    np_image = np.array(pil_image).astype(np.float32) / 255.0
    return torch.from_numpy(np_image).unsqueeze(0)


def create_error_image(width=512, height=512, color=(1.0, 0.0, 0.0)):
    """
    创建错误提示图像（纯色）
    
    Args:
        width: 宽度
        height: 高度
        color: RGB 颜色元组 (0-1)
    
    Returns:
        ComfyUI 格式的图像张量
    """
    error_img = np.zeros((1, height, width, 3), dtype=np.float32)
    error_img[:, :, :, 0] = color[0]
    error_img[:, :, :, 1] = color[1]
    error_img[:, :, :, 2] = color[2]
    return torch.from_numpy(error_img)
