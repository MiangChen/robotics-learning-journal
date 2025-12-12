#!/usr/bin/env python3
"""
使用 Pandoc 将 Markdown 转换为 PDF

用法:
    python3 utils/md_to_pdf_pandoc.py <input.md> [output.pdf]
    python3 utils/md_to_pdf_pandoc.py docs/任务规划/src/任务规划.md
"""

import sys
import shutil
import subprocess
from pathlib import Path


def check_pandoc():
    return shutil.which('pandoc') is not None


def check_xelatex():
    return shutil.which('xelatex') is not None


def get_cjk_font():
    fonts = ["Noto Sans CJK SC", "Noto Serif CJK SC", "WenQuanYi Micro Hei", "Source Han Sans SC"]
    try:
        result = subprocess.run(['fc-list', ':lang=zh'], capture_output=True, text=True)
        available = result.stdout.lower().replace(' ', '')
        for font in fonts:
            if font.lower().replace(' ', '') in available:
                return font
    except:
        pass
    return "Noto Sans CJK SC"


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
    
    cmd = [
        'pandoc', input_file.name,
        '-o', str(output_file),
        '--pdf-engine=xelatex',
        '-V', f'CJKmainfont={cjk_font}',
        '-V', f'mainfont={cjk_font}',
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
    
    if not check_xelatex():
        print("错误: XeLaTeX 未安装\n安装: sudo apt install texlive-xetex texlive-lang-chinese")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    
    success = convert_md_to_pdf(input_file, output_file)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
