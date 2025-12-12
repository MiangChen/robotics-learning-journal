#!/usr/bin/env python3
"""
使用 Pandoc 将 Markdown 转换为 PDF

用法:
    python3 utils/md_to_pdf_pandoc.py <input.md> [output.pdf]
"""

import sys
import re
import shutil
import subprocess
from pathlib import Path


def check_pandoc():
    return shutil.which('pandoc') is not None


def get_cjk_font():
    fonts = ["Noto Sans CJK SC", "Noto Serif CJK SC", "WenQuanYi Micro Hei"]
    try:
        result = subprocess.run(['fc-list', ':lang=zh'], capture_output=True, text=True)
        available = result.stdout.lower().replace(' ', '')
        for font in fonts:
            if font.lower().replace(' ', '') in available:
                return font
    except:
        pass
    return "Noto Sans CJK SC"


# Emoji 到文字的映射
EMOJI_MAP = {
    '📜': '▶',
    '✅': '√',
    '❌': '×',
    '🧠': '[脑]',
    '⚔': '[剑]',
    '⚙': '[齿轮]',
    '🌊': '[浪]',
    '🌋': '[火山]',
    '💎': '[宝石]',
    '💤': '[睡]',
    '🔋': '[电池]',
}


def replace_emoji(content: str) -> str:
    """将 emoji 替换为文字符号"""
    for emoji, text in EMOJI_MAP.items():
        content = content.replace(emoji, text)
    return content


def fix_indentation(content: str) -> str:
    """修复缩进问题：移除段落开头的全角空格"""
    # 移除行首的全角空格（U+3000）和普通空格混合
    content = re.sub(r'^[　\t]+', '', content, flags=re.MULTILINE)
    return content


def convert_md_to_pdf(input_file: Path, output_file: Path = None):
    if not input_file.exists():
        print(f"错误: 文件 {input_file} 不存在")
        return False
    
    if output_file is None:
        output_file = input_file.with_suffix('.pdf')
    
    cjk_font = get_cjk_font()
    print(f"使用字体: {cjk_font}")
    
    input_file = input_file.resolve()
    output_file = output_file.resolve()
    work_dir = input_file.parent
    
    # 读取并预处理内容（替换 emoji）
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = replace_emoji(content)
    content = fix_indentation(content)
    
    # 写入临时文件
    temp_file = work_dir / f'.{input_file.stem}_temp.md'
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 创建 LaTeX header 改善列表样式和超链接样式
    header = r'''
\usepackage{enumitem}
\setlist[itemize]{leftmargin=2em, itemsep=0.3em}
\setlist[itemize,2]{label=\textopenbullet, leftmargin=2em}
\setlist[itemize,3]{label=\textendash, leftmargin=2em}

% 超链接样式：蓝色+下划线
\usepackage{hyperref}
\hypersetup{
    colorlinks=false,
    linkbordercolor={0 0 1},
    urlbordercolor={0 0 1},
    pdfborderstyle={/S/U/W 1}
}
'''
    header_file = work_dir / '.pandoc_header.tex'
    with open(header_file, 'w') as f:
        f.write(header)
    
    cmd = [
        'pandoc', temp_file.name,
        '-o', str(output_file),
        '--pdf-engine=xelatex',
        '-V', f'CJKmainfont={cjk_font}',
        '-V', 'mainfont=Times New Roman',
        '-V', 'monofont=DejaVu Sans Mono',
        '-H', str(header_file),
        '--toc', '--toc-depth=3',
        '-V', 'documentclass=report',
        '-V', 'geometry:margin=2.5cm',
        '-V', 'fontsize=12pt',
        '-V', 'papersize=a4',
        '-V', 'colorlinks=true',
        '--highlight-style=tango',
        '-N',
        '--from=markdown-raw_tex',
    ]
    
    print(f"输入: {input_file}")
    print(f"输出: {output_file}")
    
    try:
        result = subprocess.run(cmd, cwd=str(work_dir), capture_output=True, text=True, timeout=300)
        
        # 清理临时文件
        if temp_file.exists():
            temp_file.unlink()
        if header_file.exists():
            header_file.unlink()
        
        if output_file.exists():
            size_kb = output_file.stat().st_size / 1024
            print(f"✓ 转换成功: {output_file}")
            print(f"  文件大小: {size_kb:.1f} KB")
            return True
        else:
            print(f"✗ 转换失败")
            if result.stderr:
                for line in result.stderr.split('\n')[-20:]:
                    if line.strip():
                        print(f"  {line}")
            return False
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print("用法: python3 md_to_pdf_pandoc.py <input.md> [output.pdf]")
        sys.exit(1)
    
    if not check_pandoc():
        print("错误: Pandoc 未安装\n安装: sudo apt install pandoc")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    
    success = convert_md_to_pdf(input_file, output_file)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
