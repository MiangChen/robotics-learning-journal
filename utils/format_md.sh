#!/bin/bash
# Markdown 文档格式化脚本
# 自动统一标点符号并更新目录

FILE="${1:-集群任务规划.md}"

echo "📝 正在格式化文档: $FILE"
echo ""

echo "1️⃣  统一标点符号..."
python3 utils/fix_punctuation.py "$FILE"
echo ""

echo "2️⃣  更新目录..."
python3 utils/generate_toc.py "$FILE"
echo ""

echo "✅ 文档格式化完成！"
