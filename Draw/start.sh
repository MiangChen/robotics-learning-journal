#!/bin/bash
# ComfyUI 启动入口
# 用法: bash Draw/start.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/ComfyUI"

# 激活 conda 环境（如果需要）
# source ~/miniconda3/bin/activate comfyui

python main.py --listen 0.0.0.0 --port 8188
