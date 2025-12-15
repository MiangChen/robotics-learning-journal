"""
学术插图工作流节点
"""

import requests
import numpy as np
import torch
from PIL import Image
import io
import base64

from .config import load_config
from .constants import LAYOUT_TYPES
from .prompts import ARCHITECT_PROMPT, RENDERER_PROMPT
from .utils import image_to_base64, parse_image_from_response, bytes_to_tensor, create_error_image


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
        
        full_prompt = ARCHITECT_PROMPT + paper_content
        if custom_instructions:
            full_prompt += f"\n\n# Additional Instructions\n{custom_instructions}"
        full_prompt += f"\n\n# Hints\n- 建议使用 {layout_hint} 布局\n- 建议划分 {zone_count} 个区域"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        
        payload = {
            "model": "gemini-3-pro-preview",
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

    def render(self, visual_schema, color_palette="", **kwargs):
        config = load_config()
        api_key = config.get("api_key", "")
        url = config.get("api_url", "https://vip.dmxapi.com/v1/chat/completions")
        model_type = config.get("default_model", "gemini-3-pro-image-preview")
        
        if not api_key:
            return (create_error_image(), "错误: 未配置 API Key")
        
        schema_content = visual_schema
        if "---BEGIN PROMPT---" in visual_schema and "---END PROMPT---" in visual_schema:
            start = visual_schema.find("---BEGIN PROMPT---") + len("---BEGIN PROMPT---")
            end = visual_schema.find("---END PROMPT---")
            schema_content = visual_schema[start:end].strip()
        
        max_schema_len = 4000
        if len(schema_content) > max_schema_len:
            print(f"[Renderer] Schema 过长 ({len(schema_content)} chars)，截断至 {max_schema_len}")
            schema_content = schema_content[:max_schema_len] + "\n...(truncated)"
        
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
        
        max_ref_images = 2
        ref_count = 0
        for i in range(1, 9):
            if ref_count >= max_ref_images:
                break
            ref_img = kwargs.get(f"ref_image_{i}")
            if ref_img is not None:
                img_base64 = image_to_base64(ref_img, format="JPEG", max_size=800, quality=85)
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
        
        print(f"[Renderer] ========== 请求详情 ==========")
        print(f"[Renderer] URL: {url}")
        print(f"[Renderer] Model: {model_type}")
        print(f"[Renderer] API Key: {api_key[:10]}...{api_key[-4:]}")
        print(f"[Renderer] Prompt 长度: {len(render_prompt)} chars")
        print(f"[Renderer] 参考图数量: {ref_count}")
        print(f"[Renderer] ================================")
        
        try:
            print("[Renderer] 正在发送请求...")
            response = requests.post(url, headers=headers, json=payload, timeout=180)
            print(f"[Renderer] 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                resp_content = result["choices"][0]["message"]["content"]
                
                image_bytes = parse_image_from_response(resp_content)
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
        return (create_error_image(), info_text)


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
                "enabled": ("BOOLEAN", {"default": True}),
            },
        }
    
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "info")
    FUNCTION = "edit"
    CATEGORY = "DMXAPI/Academic"

    def edit(self, image, edit_instruction, enabled=True):
        if not enabled:
            print("[Editor] 已停用，跳过编辑")
            empty_img = np.zeros((1, 512, 512, 3), dtype=np.float32)
            return (torch.from_numpy(empty_img), "已停用")
        
        config = load_config()
        api_key = config.get("api_key", "")
        url = config.get("api_url", "https://vip.dmxapi.com/v1/chat/completions")
        model_type = config.get("default_model", "gemini-3-pro-image-preview")
        
        if not api_key:
            return (image, "错误: 未配置 API Key")
        
        img_base64 = image_to_base64(image)
        
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
                
                image_bytes = parse_image_from_response(resp_content)
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
