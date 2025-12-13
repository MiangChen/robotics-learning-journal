# Draw - AI 绘图工具集

本目录集成了 AI 图像生成相关的工具和工作流。

## 目录结构

```
Draw/
├── README.md           # 本文档
├── start.sh            # ComfyUI 启动脚本
├── ComfyUI/            # ComfyUI 核心
│   ├── custom_nodes/   # 自定义节点
│   │   └── comfyui_dmxapi/  # Gemini API 插件
│   └── my_workflows/   # 自定义工作流
└── examples/           # 使用案例
```

## 快速开始

### 启动 ComfyUI

```bash
bash Draw/start.sh
```

然后访问 http://localhost:8188

### 自定义插件

#### Gemini API 插件 (comfyui_dmxapi)

位置: `ComfyUI/custom_nodes/comfyui_dmxapi/`

功能:
- 调用 Google Gemini API 进行图像生成/理解
- 支持多图输入

使用前需要设置环境变量:
```bash
export GEMINI_API_KEY="your-api-key"
```

## 工作流案例

### 1. Gemini 基础工作流

文件: `ComfyUI/my_workflows/dmxapi_gemini_basic.json`

用途: 使用 Gemini API 进行基础图像生成

### 2. 多图输入工作流

文件: `ComfyUI/my_workflows/dmxapi_multi_image.json`

用途: 多图输入的 Gemini 处理流程

## 添加新工作流

1. 在 ComfyUI 界面中设计工作流
2. 保存到 `ComfyUI/my_workflows/` 目录
3. 在本文档中添加说明
