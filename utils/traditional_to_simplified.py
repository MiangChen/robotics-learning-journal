#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
繁体字转简体字工具
- 自动将Markdown文档中的繁体字转换为简体字
- 保护代码块、链接、图片路径等特殊内容
- 支持预览模式
"""

import sys
import os
import re


def check_dependencies():
    """检查依赖是否安装"""
    try:
        import opencc
        return True
    except ImportError:
        print("❌ 缺少 opencc-python-reimplemented 包")
        print("\n安装方法：")
        print("  pip install opencc-python-reimplemented")
        return False


def extract_protected_blocks(content):
    """提取需要保护的代码块和特殊内容"""
    protected_blocks = []
    
    # 保护代码块（使用非贪婪匹配，并确保匹配完整的代码块）
    code_block_pattern = r'```[^\n]*\n[\s\S]*?```'
    for match in re.finditer(code_block_pattern, content):
        protected_blocks.append((match.start(), match.end(), match.group()))
    
    # 保护行内代码（排除已经在代码块中的部分）
    inline_code_pattern = r'`[^`\n]+`'
    for match in re.finditer(inline_code_pattern, content):
        # 检查是否在已保护的代码块中
        in_protected = False
        for start, end, _ in protected_blocks:
            if start <= match.start() < end:
                in_protected = True
                break
        if not in_protected:
            protected_blocks.append((match.start(), match.end(), match.group()))
    
    # 保护图片（必须在链接之前处理）
    image_pattern = r'!\[([^\]]*)\]\(([^\)]+)\)'
    for match in re.finditer(image_pattern, content):
        protected_blocks.append((match.start(), match.end(), match.group()))
    
    # 保护链接
    link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    for match in re.finditer(link_pattern, content):
        # 检查是否已经被图片保护
        in_protected = False
        for start, end, _ in protected_blocks:
            if start <= match.start() < end:
                in_protected = True
                break
        if not in_protected:
            protected_blocks.append((match.start(), match.end(), match.group()))
    
    # 保护HTML标签
    html_pattern = r'<[^>]+>'
    for match in re.finditer(html_pattern, content):
        protected_blocks.append((match.start(), match.end(), match.group()))
    
    # 按位置排序，去重
    protected_blocks.sort(key=lambda x: x[0])
    
    # 去除重叠的保护块（保留更大的）
    filtered_blocks = []
    for block in protected_blocks:
        if not filtered_blocks:
            filtered_blocks.append(block)
        else:
            last_start, last_end, _ = filtered_blocks[-1]
            curr_start, curr_end, _ = block
            # 如果当前块与上一个块重叠
            if curr_start < last_end:
                # 保留更大的块
                if curr_end > last_end:
                    filtered_blocks[-1] = block
            else:
                filtered_blocks.append(block)
    
    return filtered_blocks


def convert_traditional_to_simplified(content):
    """将繁体字转换为简体字，保护特殊内容"""
    try:
        from opencc import OpenCC
        
        # 创建繁体到简体的转换器
        cc = OpenCC('t2s')  # t2s = Traditional to Simplified
        
        # 提取需要保护的内容
        protected_blocks = extract_protected_blocks(content)
        
        # 如果没有需要保护的内容，直接转换
        if not protected_blocks:
            return cc.convert(content)
        
        # 分段处理
        result = []
        last_end = 0
        
        for start, end, original in protected_blocks:
            # 转换保护块之前的内容
            if start > last_end:
                text_to_convert = content[last_end:start]
                result.append(cc.convert(text_to_convert))
            
            # 保留原始保护块
            result.append(original)
            last_end = end
        
        # 转换最后一段
        if last_end < len(content):
            result.append(cc.convert(content[last_end:]))
        
        return ''.join(result)
        
    except Exception as e:
        print(f"❌ 转换失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def process_file(input_file, output_file=None, preview=False):
    """处理Markdown文件，转换繁体字为简体字"""
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
        
        # 转换繁体字为简体字
        converted_content = convert_traditional_to_simplified(content)
        
        if converted_content is None:
            return False
        
        # 统计实际转换的字符（只统计真正改变的位置）
        changed_count = 0
        changed_chars = set()
        for i, (orig_char, conv_char) in enumerate(zip(content, converted_content)):
            if orig_char != conv_char:
                changed_count += 1
                changed_chars.add(orig_char)
        
        if preview:
            print("\n" + "="*50)
            print("预览模式 - 显示前500个字符")
            print("="*50)
            print(converted_content[:500])
            print("="*50)
            if changed_count > 0:
                print(f"\n✓ 检测到 {changed_count} 处繁体字被转换")
                if changed_chars:
                    sample = list(changed_chars)[:20]
                    print(f"  转换的字: {' '.join(sample)}")
            else:
                print("\n✓ 未检测到需要转换的繁体字")
            return True
        
        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(converted_content)
        
        print(f"✅ 转换完成: {output_file}")
        if changed_count > 0:
            print(f"   转换了 {changed_count} 处繁体字")
            if changed_chars and len(changed_chars) <= 30:
                print(f"   转换的字: {' '.join(sorted(changed_chars))}")
        else:
            print("   未检测到繁体字")
        
        return True
        
    except Exception as e:
        print(f"❌ 处理失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    if '--help' in sys.argv or '-h' in sys.argv:
        print("""
繁体字转简体字工具

用法：
  python3 traditional_to_simplified.py [输入文件] [输出文件] [选项]
  
选项：
  --help, -h       显示帮助
  --preview, -p    预览模式（不修改文件）
  --check          检查依赖是否安装
  
示例：
  python3 traditional_to_simplified.py 文档.md              # 直接修改原文件
  python3 traditional_to_simplified.py input.md output.md  # 输出到新文件
  python3 traditional_to_simplified.py 文档.md --preview    # 预览转换结果
  python3 traditional_to_simplified.py --check             # 检查依赖

依赖安装：
  pip install opencc-python-reimplemented
        """)
        return
    
    if '--check' in sys.argv:
        if check_dependencies():
            print("✅ 依赖已安装")
        else:
            sys.exit(1)
        return
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 解析参数
    preview = '--preview' in sys.argv or '-p' in sys.argv
    
    # 获取文件路径
    args = [arg for arg in sys.argv[1:] if not arg.startswith('-')]
    
    if len(args) == 0:
        input_file = 'docs/集群任务规划.md'
        output_file = None
    elif len(args) == 1:
        input_file = args[0]
        output_file = None
    else:
        input_file = args[0]
        output_file = args[1]
    
    # 处理文件
    success = process_file(input_file, output_file, preview)
    
    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main()
