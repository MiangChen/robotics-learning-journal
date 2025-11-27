#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为Markdown文档的普通段落添加缩进
- 在普通文字段落前添加全角空格缩进（避免被识别为代码块）
- 保护标题、代码块、列表、引用、链接等特殊格式
- 先清理段落开头的所有空白字符，再统一添加全角空格
"""

import sys
import os
import re


def should_add_indent(line, in_code_block):
    """判断是否应该为该行添加缩进
    
    返回：
        True: 需要添加缩进（普通段落）
        False: 跳过该行（特殊格式或空行）
    """
    stripped = line.strip()
    
    # 空行不处理
    if not stripped:
        return False
    
    # 代码块内不处理
    if in_code_block:
        return False
    
    # 标题不处理（# 开头）
    if re.match(r'^#{1,6}\s', stripped):
        return False
    
    # 列表不处理（- 或 * 或数字. 开头）
    if re.match(r'^[-*]\s', stripped) or re.match(r'^\d+\.\s', stripped):
        return False
    
    # 引用不处理（> 开头）
    if stripped.startswith('>'):
        return False
    
    # 表格不处理（| 开头或包含 |）
    if stripped.startswith('|') or '|' in stripped:
        return False
    
    # HTML标签不处理（< 开头）
    if stripped.startswith('<'):
        return False
    
    # 图片不处理（![ 开头）
    if stripped.startswith('!['):
        return False
    
    # 链接行不处理（纯链接行）
    if re.match(r'^https?://', stripped):
        return False
    
    # 分页符不处理
    if 'page-break' in line:
        return False
    
    # 水平线不处理（--- 或 *** 或 ___）
    if re.match(r'^[-*_]{3,}$', stripped):
        return False
    
    # 判断是否是中文或英文段落
    has_chinese = bool(re.search(r'[\u4e00-\u9fff]', stripped))
    has_english = bool(re.search(r'[a-zA-Z]', stripped))
    
    # 只对包含文字内容的行添加缩进
    if has_chinese or has_english:
        return True
    
    return False


def add_indent(content, indent_type='fullwidth'):
    """为普通段落添加缩进
    
    策略：先清理段落开头的所有空白字符，再统一添加全角空格
    
    Args:
        content: 文档内容
        indent_type: 缩进类型
            - 'fullwidth': 使用两个全角空格（默认，推荐用于中文）
            - 'html': 使用 HTML 实体 &emsp;&emsp;
    
    Returns:
        (new_content, stats): 处理后的内容和统计信息
    """
    lines = content.split('\n')
    result_lines = []
    in_code_block = False
    
    # 定义缩进字符
    if indent_type == 'html':
        indent_str = '&emsp;&emsp;'
    else:  # fullwidth
        # 使用两个全角空格（U+3000）
        indent_str = '　　'
    
    # 统计信息
    stats = {
        'processed': 0,  # 处理的段落数（清理+添加缩进）
        'skipped': 0     # 跳过的行数
    }
    
    for line in lines:
        # 检测代码块
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            result_lines.append(line)
            stats['skipped'] += 1
            continue
        
        # 判断是否需要添加缩进
        if should_add_indent(line, in_code_block):
            # 先清理开头的所有空白字符（空格、Tab、全角空格等）
            cleaned = line.lstrip()
            # 再添加统一的缩进
            result_lines.append(indent_str + cleaned)
            stats['processed'] += 1
        else:
            # 保持原样
            result_lines.append(line)
            if line.strip():  # 非空行才计入跳过
                stats['skipped'] += 1
    
    return '\n'.join(result_lines), stats


def process_file(input_file, output_file=None, indent_type='fullwidth'):
    """处理Markdown文件，添加段落缩进"""
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"❌ 错误：找不到文件 {input_file}")
        return False
    
    # 如果没有指定输出文件，则覆盖原文件
    if output_file is None:
        output_file = input_file
    
    print(f"📄 正在处理: {input_file}")
    
    try:
        # 读取文件
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 添加缩进
        new_content, stats = add_indent(content, indent_type)
        
        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        indent_name = "全角空格" if indent_type == 'fullwidth' else "HTML实体"
        print(f"✅ 处理完成: {output_file}")
        print(f"   使用 {indent_name}:")
        print(f"   - 处理段落: {stats['processed']} 个（清理旧缩进 + 添加新缩进）")
        print(f"   - 跳过内容: {stats['skipped']} 行（标题、列表、代码块等）")
        return True
        
    except Exception as e:
        print(f"❌ 处理失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    if '--help' in sys.argv or '-h' in sys.argv:
        print("""
用法：
  python3 add_paragraph_indent.py [输入文件] [输出文件] [选项]
  
说明：
  为Markdown文档的普通段落添加缩进（使用全角空格，不会被识别为代码块）
  自动识别并保护标题、代码块、列表、引用等特殊格式
  
处理策略：
  1. 先清理段落开头的所有空白字符（空格、Tab、全角空格等）
  2. 再统一添加全角空格缩进
  3. 这样可以确保缩进格式统一，不会重复添加
  
选项：
  --help, -h       显示帮助
  --html           使用HTML实体（&emsp;&emsp;）而非全角空格
  
示例：
  python3 add_paragraph_indent.py                      # 处理默认文件，使用全角空格
  python3 add_paragraph_indent.py 文档.md              # 直接修改原文件
  python3 add_paragraph_indent.py input.md output.md  # 输出到新文件
  python3 add_paragraph_indent.py 文档.md --html       # 使用HTML实体缩进
  
注意：
  - 默认使用两个全角空格（　　）作为缩进，适合中文排版
  - 全角空格不会被Markdown解释为代码块
  - 会先清理段落开头的所有空白字符，再添加统一的缩进
  - 多次运行不会重复添加缩进（幂等操作）
  - 如果需要在某些特殊环境下使用，可以选择 --html 选项
        """)
        return
    
    # 解析参数
    indent_type = 'fullwidth'
    if '--html' in sys.argv:
        indent_type = 'html'
        sys.argv.remove('--html')
    
    # 获取文件路径
    if len(sys.argv) > 1 and not sys.argv[1].startswith('--'):
        input_file = sys.argv[1]
    else:
        input_file = 'docs/任务规划.md'
    
    output_file = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else None
    
    # 处理文件
    success = process_file(input_file, output_file, indent_type)
    
    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main()