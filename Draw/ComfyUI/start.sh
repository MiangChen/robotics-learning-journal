#!/bin/bash

# ComfyUI 启动脚本

cd "$(dirname "$0")"

# 激活 conda 环境
source ~/anaconda3/etc/profile.d/conda.sh 2>/dev/null || \
source ~/miniconda3/etc/profile.d/conda.sh 2>/dev/null || \
source /opt/conda/etc/profile.d/conda.sh 2>/dev/null

conda activate base

echo "=========================================="
echo "  ComfyUI 启动中..."
echo "  访问地址: http://localhost:8188"
echo "=========================================="

python main.py --listen 0.0.0.0 --default-workflow my_workflows/academic_diagram.json "$@"
