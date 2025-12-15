"""
ComfyUI 自定义节点 - 学术插图工作流
"""

from .nodes_academic import (
    AcademicArchitect,
    AcademicRenderer,
    AcademicEditor,
)

# 节点注册
NODE_CLASS_MAPPINGS = {
    "AcademicArchitect": AcademicArchitect,
    "AcademicRenderer": AcademicRenderer,
    "AcademicEditor": AcademicEditor,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AcademicArchitect": "学术插图 - 逻辑构建 (Architect)",
    "AcademicRenderer": "学术插图 - 视觉渲染 (Renderer)",
    "AcademicEditor": "学术插图 - 交互编辑 (Editor)",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
