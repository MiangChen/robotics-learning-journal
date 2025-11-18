#!/bin/bash
# Markdown 文档格式化脚本
# 自动统一标点符号、更新目录并转换为PDF

FILE="${1:-集群任务规划.md}"

echo "📝 正在处理文档: $FILE"
echo ""

# 检查并安装PDF转换依赖
echo "🔍 检查依赖..."
python3 -c "import markdown, weasyprint, pygments" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 安装PDF转换依赖..."
    pip install markdown weasyprint pygments
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败，将跳过PDF转换步骤"
        SKIP_PDF=1
    else
        echo "✅ 依赖安装成功"
    fi
fi
echo ""

echo "1️⃣  统一标点符号..."
python3 utils/fix_punctuation.py "$FILE"
echo ""

echo "2️⃣  更新目录..."
python3 utils/generate_toc.py "$FILE"
echo ""

if [ -z "$SKIP_PDF" ]; then
    echo "3️⃣  转换为PDF..."
    python3 utils/md_to_pdf.py "$FILE"
    echo ""
fi

echo "✅ 文档处理完成！"
