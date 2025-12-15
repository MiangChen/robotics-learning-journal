# 学术插图 AI 绘制工作流

## 环境配置

```bash
# 1. 安装依赖
bash Draw/setup.sh

# 2. 编辑配置文件，填入 API Key 和 Base URL, 以及要用的模型名称
Draw/config_llm.json

# 3. 启动 ComfyUI
bash Draw/start.sh
```

## 访问

http://localhost:8188

`Ctrl + O` 打开加载 workflow 的界面

![open.png](./asset/open_folder.png)

选择 `Draw/ComfyUI/workflows/academic_diagram.json`

![image-20251215233812328](./asset/README.asset/image-20251215233812328.png)

然后就可以看到该工作流：

![image-20251215233857972](./asset/README.asset/image-20251215233857972.png)

## 工作流概览

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Step 1         │    │  Step 2         │    │  Step 3         │
│  The Architect  │ -> │  The Renderer   │ -> │  The Editor     │
│  逻辑构建       │    │  视觉渲染       │    │  交互式微调     │
│  (Gemini/GPT)   │    │  (Nano-Banana)  │    │  (自然语言编辑) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```
