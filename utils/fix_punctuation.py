#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一Markdown文件中的标点符号
- 将英文逗号替换为中文逗号
- 将中文句子结尾的英文句号替换为中文句号
- 保护代码块、链接、图片路径等不被修改
"""

import re
import sys


def fix_punctuation(content):
    """修复标点符号"""
    lines = content.split('\n')
    result_lines = []
    in_code_block = False
    
    for line in lines:
        # 检测代码块
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            result_lines.append(line)
            continue
        
        # 代码块内不处理
        if in_code_block:
            result_lines.append(line)
            continue
        
        # 跳过链接行（以 - http 或 - https 开头）
        if re.match(r'^\s*-\s*https?://', line):
            result_lines.append(line)
            continue
        
        # 跳过图片行
        if '![' in line and '](' in line:
            result_lines.append(line)
            continue
        
        # 跳过纯英文行（包含大量英文字母和空格的行）
        if line.strip():
            ascii_count = sum(1 for c in line if ord(c) < 128)
            if ascii_count / len(line) > 0.7:
                result_lines.append(line)
                continue
        
        # 处理标点符号
        processed_line = line
        
        # 1. 替换英文逗号为中文逗号
        # 使用正则表达式，只替换中文字符附近的英文逗号
        temp_line = re.sub(r'([\u4e00-\u9fff])\s*,\s*', r'\1，', processed_line)
        temp_line = re.sub(r',\s*([\u4e00-\u9fff])', r'，\1', temp_line)
        processed_line = temp_line
        
        # 2. 替换中文句子结尾的英文句号为中文句号
        processed_line = re.sub(r'([\u4e00-\u9fff])\s*\.\s*$', r'\1。', processed_line)
        processed_line = re.sub(r'([\u4e00-\u9fff])\s*\.\s+', r'\1。 ', processed_line)
        
        # 3. 处理中文字符后跟英文句号的情况（句中）
        processed_line = re.sub(r'([\u4e00-\u9fff])\.\s+([\u4e00-\u9fff])', r'\1。\2', processed_line)
        
        result_lines.append(processed_line)
    
    return '\n'.join(result_lines)


def main():
    # 获取文件路径
    if len(sys.argv) > 1 and sys.argv[1] not in ['--help', '-h']:
        input_file = sys.argv[1]
    else:
        input_file = '集群任务规划.md'
    
    if '--help' in sys.argv or '-h' in sys.argv:
        print("""
用法：
  python3 fix_punctuation.py [文件名]
  
示例：
  python3 fix_punctuation.py                # 处理默认文件
  python3 fix_punctuation.py 集群任务规划.md  # 处理指定文件
        """)
        return
    
    # 读取文件
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"错误：找不到文件 {input_file}")
        sys.exit(1)
    
    # 处理标点符号
    fixed_content = fix_punctuation(content)
    
    # 写入文件
    with open(input_file, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"✓ 标点符号已统一，文件已保存到: {input_file}")
    
    # 统计修改
    original_commas = content.count(',')
    fixed_commas = fixed_content.count(',')
    chinese_commas = fixed_content.count('，')
    
    original_periods = content.count('.')
    fixed_periods = fixed_content.count('.')
    chinese_periods = fixed_content.count('。')
    
    print(f"\n统计信息:")
    print(f"  英文逗号: {original_commas} → {fixed_commas}")
    print(f"  中文逗号: {chinese_commas}")
    print(f"  英文句号: {original_periods} → {fixed_periods}")
    print(f"  中文句号: {chinese_periods}")


if __name__ == '__main__':
    main()
