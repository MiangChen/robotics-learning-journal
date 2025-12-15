"""
ComfyUI 自定义节点 - DMXAPI Gemini 图像生成
"""

from .nodes_basic import (
    DMXAPIGeminiImageGen,
    DMXAPIGeminiImageEdit,
    DMXAPIGeminiMultiImage,
    DMXAPIGeminiImageBatch,
)

from .nodes_styled import (
    DMXAPIGeminiStyled,
    DMXAPIStyleTransfer,
)

from .nodes_academic import (
    AcademicArchitect,
    AcademicRenderer,
    AcademicEditor,
)

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

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
