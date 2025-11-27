#!/bin/bash
# Markdown 文档格式化脚本
# 自动繁简转换、统一标点符号、更新目录、添加分页符，可选转换为PDF
#
# 用法：
#   ./format_md.sh [文件名] [-pdf]
#
# 示例：
#   ./format_md.sh                                    # 处理默认文件（docs/任务规划.md），不转PDF
#   ./format_md.sh docs/任务规划.md                 # 处理指定文件，不转PDF
#   ./format_md.sh -pdf                               # 处理默认文件并转PDF
#   ./format_md.sh docs/任务规划.md -pdf            # 处理指定文件并转PDF
#
# 处理流程：
#   1. 繁体字转简体字
#   2. 统一标点符号
#   3. 添加段落缩进
#   4. 更新目录
#   5. 添加分页符
#   6. 转换为PDF（可选）

# 解析参数
FILE=""
CONVERT_PDF=0

for arg in "$@"; do
    case $arg in
        -pdf|--pdf)
            CONVERT_PDF=1
            shift
            ;;
        *)
            if [ -z "$FILE" ]; then
                FILE="$arg"
            fi
            ;;
    esac
done

# 如果没有指定文件，使用默认文件
if [ -z "$FILE" ]; then
    FILE="docs/任务规划.md"
fi

echo "📝 正在处理文档: $FILE"
echo ""

echo "1️⃣  繁体字转简体字..."
python3 utils/traditional_to_simplified.py "$FILE"
echo ""

echo "2️⃣  统一标点符号..."
python3 utils/fix_punctuation.py "$FILE"
echo ""

echo "3️⃣  添加段落缩进..."
python3 utils/add_paragraph_indent.py "$FILE"
echo ""

echo "4️⃣  更新目录..."
python3 utils/generate_toc.py "$FILE"
echo ""

echo "5️⃣  添加分页符..."
python3 utils/auto_divide.py "$FILE"
echo ""

if [ $CONVERT_PDF -eq 1 ]; then
    echo "6️⃣  转换为PDF..."
    
    # 检查PDF转换依赖
    python3 -c "import markdown, weasyprint, pygments" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "📦 安装PDF转换依赖..."
        pip install markdown weasyprint pygments
        if [ $? -ne 0 ]; then
            echo "❌ 依赖安装失败，跳过PDF转换"
        else
            echo "✅ 依赖安装成功"
            python3 utils/md_to_pdf.py "$FILE"
        fi
    else
        python3 utils/md_to_pdf.py "$FILE"
    fi
    echo ""
fi

echo "✅ 文档处理完成！"
