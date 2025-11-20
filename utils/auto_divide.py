#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动在一级和二级标题前添加分页符
- 在 # 和 ## 标题前添加 <div style="page-break-after: always;"></div>
- 如果已经存在分页符，则不重复添加
- 保持文档开头的第一个标题不添加分页符
"""

import sys
import os
import re


def add_page_breaks(content):
    """在一级和二级标题前添加分页符"""
    lines = content.split('\n')
    result = []
    
    # 分页符标记
    page_break = '<div style="page-break-after: always;"></div>'
    
    # 标记是否是文档开头（跳过前面的空行和注释）
    is_first_heading = True
    
    for i, line in enumerate(lines):
        # 检查是否是一级或二级标题
        is_h1 = line.strip().startswith('# ') and not line.strip().startswith('## ')
        is_h2 = line.strip().startswith('## ') and not line.strip().startswith('### ')
        
        if is_h1 or is_h2:
            # 如果是文档中的第一个标题，不添加分页符
            if is_first_heading:
                is_first_heading = False
                result.append(line)
                continue
            
            # 检查前面是否已经有分页符
            has_page_break = False
            
            # 向前查找最近的非空行
            for j in range(len(result) - 1, -1, -1):
                prev_line = result[j].strip()
                if prev_line:
                    # 如果前面已经有分页符，不重复添加
                    if 'page-break' in prev_line:
                        has_page_break = True
                    break
            
            # 如果没有分页符，添加一个
            if not has_page_break:
                # 在标题前添加空行和分页符
                if result and result[-1].strip():  # 如果前一行不是空行
                    result.append('')
                result.append(page_break)
                result.append('')
            
            result.append(line)
        else:
            # 非标题行，直接添加
            result.append(line)
            
            # 如果遇到非空行且不是注释，标记已经过了文档开头
            if line.strip() and not line.strip().startswith('<!--'):
                if not (line.strip().startswith('#') or 'page-break' in line):
                    # 如果这行不是标题也不是分页符，说明有内容了
                    pass
    
    return '\n'.join(result)


def process_file(input_file, output_file=None):
    """处理Markdown文件，添加分页符"""
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
        
        # 添加分页符
        new_content = add_page_breaks(content)
        
        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ 处理完成: {output_file}")
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
  python3 auto_divide.py [输入文件] [输出文件]
  
说明：
  在一级和二级标题前自动添加分页符，用于 Typora 导出 PDF
  
选项：
  --help, -h       显示帮助
  
示例：
  python3 auto_divide.py 集群任务规划.md              # 直接修改原文件
  python3 auto_divide.py input.md output.md        # 输出到新文件
        """)
        return
    
    # 获取文件路径
    if len(sys.argv) > 1 and not sys.argv[1].startswith('--'):
        input_file = sys.argv[1]
    else:
        input_file = '集群任务规划.md'
    
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # 处理文件
    success = process_file(input_file, output_file)
    
    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main()
