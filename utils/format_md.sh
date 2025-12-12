#!/bin/bash
# Markdown 文档格式化脚本
# 统一标点符号
#
# 用法：
#   ./format_md.sh [文件名]
#
# 示例：
#   ./format_md.sh docs/任务规划.md

FILE="$1"

if [ -z "$FILE" ]; then
    echo "用法: ./format_md.sh <文件名>"
    echo "示例: ./format_md.sh docs/任务规划.md"
    exit 1
fi

if [ ! -f "$FILE" ]; then
    echo "❌ 文件不存在: $FILE"
    exit 1
fi

echo "📝 正在处理文档: $FILE"
echo ""

echo "1️⃣  统一标点符号..."
python3 utils/fix_punctuation.py "$FILE"
echo ""

echo "✅ 文档处理完成！"
