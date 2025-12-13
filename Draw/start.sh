#!/bin/bash
# ComfyUI 启动入口
# 用法: bash Draw/start.sh [--setup]
#
# 参数:
#   --setup    首次运行时安装依赖并配置 API key

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMFYUI_DIR="$SCRIPT_DIR/ComfyUI"
PLUGIN_DIR="$COMFYUI_DIR/custom_nodes/comfyui_dmxapi"
CONFIG_FILE="$PLUGIN_DIR/config.json"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== ComfyUI 启动脚本 ===${NC}"

# 首次安装函数
setup() {
    echo -e "${YELLOW}[Setup] 开始安装依赖...${NC}"
    
    # 安装 ComfyUI 依赖
    echo -e "${YELLOW}[Setup] 安装 ComfyUI requirements...${NC}"
    pip install -r "$COMFYUI_DIR/requirements.txt"
    
    # 配置 API key
    if [ ! -f "$CONFIG_FILE" ]; then
        echo -e "${YELLOW}[Setup] 配置 DMXAPI 插件...${NC}"
        echo -e "${YELLOW}请输入你的 DMXAPI API Key:${NC}"
        read -r API_KEY
        
        cat > "$CONFIG_FILE" << EOF
{
    "api_key": "$API_KEY",
    "api_url": "https://vip.dmxapi.com/v1/chat/completions",
    "default_model": "gemini-3-pro-image-preview"
}
EOF
        echo -e "${GREEN}[Setup] 配置文件已创建: $CONFIG_FILE${NC}"
    else
        echo -e "${GREEN}[Setup] 配置文件已存在，跳过${NC}"
    fi
    
    echo -e "${GREEN}[Setup] 安装完成！${NC}"
}

# 检查是否需要 setup
if [ "$1" == "--setup" ]; then
    setup
fi

# 检查配置文件
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}[警告] 未找到配置文件: $CONFIG_FILE${NC}"
    echo -e "${YELLOW}请运行: bash Draw/start.sh --setup${NC}"
    echo ""
fi

# 进入 ComfyUI 目录并启动
cd "$COMFYUI_DIR"
echo -e "${GREEN}[启动] ComfyUI @ http://localhost:8188${NC}"
python main.py --listen 0.0.0.0 --port 8188
