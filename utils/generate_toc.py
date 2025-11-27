#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动生成Markdown文档的目录
- 扫描所有标题（##, ###, ####, #####）
- 生成带缩进的目录结构
- 自动生成锚点链接
"""

import re
import sys
import os


def generate_anchor(title):
    """
    根据标题生成GitHub风格的锚点
    规则：
    1. 转小写
    2. 移除特殊字符，保留字母、数字、中文、空格、连字符
    3. 空格替换为连字符
    4. 连续的连字符保持不变（GitHub的行为）
    """
    title = title.strip()
    anchor = title.lower()
    
    # 移除特殊字符，保留字母、数字、中文、空格、连字符
    # 注意：这里不移除连字符
    anchor = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', anchor)
    
    # 空格替换为连字符
    anchor = re.sub(r'\s+', '-', anchor)
    
    # 注意：不要合并多个连字符！GitHub会保留它们
    # 例如："任务 - 分配" -> "任务---分配" (空格变成-, 原有的-保留)
    
    # 移除首尾的连字符
    anchor = anchor.strip('-')
    
    return anchor


def extract_headings(content):
    """
    提取文档中的所有标题
    返回：[(level, title, anchor), ...]
    """
    headings = []
    lines = content.split('\n')
    in_code_block = False
    
    for line in lines:
        # 检测代码块
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            continue
        
        # 跳过代码块内的内容
        if in_code_block:
            continue
        
        # 匹配标题行：## 标题
        match = re.match(r'^(#{2,5})\s+(.+)$', line)
        if match:
            level = len(match.group(1))
            title = match.group(2).strip()
            
            # 移除标题中的Markdown链接语法
            title = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', title)
            
            # 移除标题中的粗体标记
            title = re.sub(r'\*\*(.+?)\*\*', r'\1', title)
            
            # 生成锚点
            anchor = generate_anchor(title)
            
            headings.append((level, title, anchor))
    
    return headings


def generate_toc(headings, start_level=2, max_level=5):
    """
    生成目录
    start_level: 从哪个级别开始（默认2，即##）
    max_level: 最大级别（默认5，即#####）
    """
    toc_lines = []
    toc_lines.append("## 目录\n")
    
    for level, title, anchor in headings:
        # 只处理指定范围内的标题
        if level < start_level or level > max_level:
            continue
        
        # 计算缩进（每级2个空格）
        indent = '  ' * (level - start_level)
        
        # 生成目录项
        toc_line = f"{indent}- [{title}](#{anchor})"
        toc_lines.append(toc_line)
    
    return '\n'.join(toc_lines)


def find_toc_position(content):
    """
    查找目录的位置
    返回：(start_line, end_line) 或 None
    """
    lines = content.split('\n')
    start_line = None
    end_line = None
    
    for i, line in enumerate(lines):
        # 找到"## 目录"
        if re.match(r'^##\s+目录\s*$', line):
            start_line = i
            # 从目录开始往下找，直到遇到下一个##标题或***分隔符
            for j in range(i + 1, len(lines)):
                if re.match(r'^##\s+', lines[j]) or lines[j].strip() == '***':
                    end_line = j
                    break
            # 如果没找到结束位置，就到文件末尾
            if end_line is None:
                end_line = len(lines)
            break
    
    return (start_line, end_line) if start_line is not None else None


def update_toc(content):
    """
    更新文档中的目录
    """
    # 提取所有标题
    headings = extract_headings(content)
    
    if not headings:
        print("警告：文档中没有找到标题")
        return content
    
    # 生成新目录
    new_toc = generate_toc(headings)
    
    # 查找现有目录位置
    toc_position = find_toc_position(content)
    
    lines = content.split('\n')
    
    if toc_position:
        # 替换现有目录
        start_line, end_line = toc_position
        new_lines = lines[:start_line] + [new_toc] + lines[end_line:]
        print(f"✓ 已更新现有目录（第{start_line + 1}行）")
    else:
        # 在文档开头插入目录（在第一个##标题之前）
        insert_pos = 0
        for i, line in enumerate(lines):
            if re.match(r'^##\s+', line):
                insert_pos = i
                break
        
        new_lines = lines[:insert_pos] + [new_toc, '\n***\n'] + lines[insert_pos:]
        print(f"✓ 已在第{insert_pos + 1}行插入新目录")
    
    return '\n'.join(new_lines)


def print_toc_preview(headings):
    """
    打印目录预览
    """
    print("\n目录预览：")
    print("=" * 60)
    toc = generate_toc(headings)
    print(toc)
    print("=" * 60)
    print(f"\n共找到 {len(headings)} 个标题")


def main():
    # 获取文件路径
    if len(sys.argv) > 1 and sys.argv[1] not in ['--preview', '-p', '--help', '-h']:
        input_file = sys.argv[1]
    else:
        # 默认文件
        input_file = '任务规划.md'
    
    # 检查命令行参数
    preview_mode = '--preview' in sys.argv or '-p' in sys.argv
    
    if '--help' in sys.argv or '-h' in sys.argv:
        print("""
用法：
  python3 generate_toc.py [文件名] [选项]
  
选项：
  --preview, -p    预览目录（不修改文件）
  --help, -h       显示帮助
  
示例：
  python3 generate_toc.py                    # 更新默认文件
  python3 generate_toc.py 任务规划.md      # 更新指定文件
  python3 generate_toc.py --preview          # 预览模式
        """)
        return
    
    # 读取文件
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"错误：找不到文件 {input_file}")
        sys.exit(1)
    
    # 提取标题
    headings = extract_headings(content)
    
    if not headings:
        print("错误：文档中没有找到标题")
        sys.exit(1)
    
    # 预览模式
    if preview_mode:
        print_toc_preview(headings)
        return
    
    # 更新目录
    updated_content = update_toc(content)
    
    # 写入文件
    with open(input_file, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"✓ 目录已更新，文件已保存到: {input_file}")
    print(f"  共处理 {len(headings)} 个标题")
    
    # 显示标题统计
    level_count = {}
    for level, _, _ in headings:
        level_count[level] = level_count.get(level, 0) + 1
    
    print("\n标题统计：")
    for level in sorted(level_count.keys()):
        print(f"  {'#' * level} 标题: {level_count[level]} 个")


if __name__ == '__main__':
    main()
