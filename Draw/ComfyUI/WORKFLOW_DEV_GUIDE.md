# ComfyUI 工作流开发指南

## 1. 项目结构

```
ComfyUI/
├── models/                    # 模型文件
│   ├── checkpoints/          # SD 主模型 (.safetensors)
│   ├── loras/                # LoRA 模型
│   ├── vae/                  # VAE 模型
│   ├── controlnet/           # ControlNet 模型
│   ├── upscale_models/       # 超分模型
│   └── clip/                 # CLIP 模型
├── custom_nodes/             # 自定义节点（插件）
├── input/                    # 输入图片
├── output/                   # 生成结果
├── workflows/                # 工作流 JSON 文件（建议新建）
└── my_workflows/             # 你的自定义工作流（建议新建）
```

## 2. Git 管理策略

### 2.1 初始化你的工作流仓库
```bash
mkdir my_workflows && cd my_workflows
git init
```

### 2.2 .gitignore 配置
```gitignore
# 忽略大模型文件
*.safetensors
*.ckpt
*.pt
*.pth
*.bin

# 忽略生成的图片（可选）
output/

# 保留工作流 JSON
!*.json
```


### 2.3 推荐的 Git 工作流
```bash
# 保存工作流时导出 JSON
# 在 ComfyUI 界面: 右键 -> Save (API Format) 或 Ctrl+S

# 提交工作流
git add workflows/*.json
git commit -m "feat: 添加文生图基础工作流"
```

## 3. 必装自定义节点

在 `custom_nodes/` 目录下 clone：

```bash
cd custom_nodes

# ComfyUI Manager - 节点管理器（必装）
git clone https://github.com/ltdrdata/ComfyUI-Manager.git

# 常用节点包
git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git
git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus.git
git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git
git clone https://github.com/pythongosssss/ComfyUI-Custom-Scripts.git
```

## 4. 基础工作流类型

| 工作流类型 | 用途 | 核心节点 |
|-----------|------|---------|
| txt2img | 文生图 | KSampler, CLIP Text Encode |
| img2img | 图生图 | Load Image, KSampler |
| inpaint | 局部重绘 | Load Image, Mask |
| controlnet | 姿态/边缘控制 | ControlNet Apply |
| upscale | 超分放大 | Upscale Model |
| video | 视频生成 | AnimateDiff, SVD |

## 5. 开发步骤

### Step 1: 下载基础模型
```bash
# 下载 SD 1.5 或 SDXL 模型到 models/checkpoints/
# 推荐: https://civitai.com/
```

### Step 2: 启动 ComfyUI
```bash
python main.py --listen 0.0.0.0
# 访问 http://localhost:8188
```

### Step 3: 创建工作流
1. 右键添加节点
2. 连接节点
3. 设置参数
4. Queue Prompt 执行
5. 导出 JSON 保存

### Step 4: 调试与优化
- 使用 Preview Image 节点查看中间结果
- 调整 CFG Scale、Steps、Sampler 参数
- 测试不同 Seed 值

## 6. API 调用

ComfyUI 支持 API 调用，可以用 Python 脚本批量生成：

```python
import requests
import json

def queue_prompt(workflow_json):
    url = "http://localhost:8188/prompt"
    response = requests.post(url, json={"prompt": workflow_json})
    return response.json()
```

## 7. 下一步行动

- [ ] 下载一个基础模型到 `models/checkpoints/`
- [ ] 安装 ComfyUI-Manager
- [ ] 创建第一个 txt2img 工作流
- [ ] 导出并保存工作流 JSON
- [ ] 尝试 API 调用自动化
