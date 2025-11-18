#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将Markdown文件转换为PDF
- 支持中文字体
- 保留代码块格式
- 支持图片和表格
- 二级标题（##）自动分页
- HTTP/HTTPS链接保持可点击
- 自动添加页码
- 使用纯Python包实现（markdown + weasyprint）
"""

import sys
import os


def check_dependencies():
    """检查依赖是否安装"""
    missing = []
    
    try:
        import markdown
    except ImportError:
        missing.append('markdown')
    
    try:
        import weasyprint
    except ImportError:
        missing.append('weasyprint')
    
    try:
        from pygments import highlight
    except ImportError:
        missing.append('pygments')
    
    if missing:
        print("❌ 缺少以下Python包：")
        for pkg in missing:
            print(f"   - {pkg}")
        print("\n安装方法：")
        print(f"  pip install {' '.join(missing)}")
        return False
    
    return True


def get_html_template(content):
    """获取HTML模板（支持中文和代码高亮）"""
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @page {{
            size: A4;
            margin: 2cm;
            @bottom-right {{
                content: counter(page) " / " counter(pages);
                font-size: 10pt;
                color: #666;
            }}
        }}
        
        body {{
            font-family: "Noto Sans CJK SC", "Microsoft YaHei", "SimSun", sans-serif;
            font-size: 12pt;
            line-height: 1.6;
            color: #333;
        }}
        
        h1 {{
            font-size: 24pt;
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
            margin-top: 30px;
            page-break-after: avoid;
        }}
        
        h2 {{
            font-size: 20pt;
            color: #34495e;
            border-bottom: 1px solid #bdc3c7;
            padding-bottom: 8px;
            margin-top: 25px;
            page-break-before: always;  /* 二级标题前自动分页 */
            page-break-after: avoid;
        }}
        
        /* 第一个h2不分页（如果是紧跟h1或在文档开头） */
        h1 + h2,
        body > h2:first-child {{
            page-break-before: auto;
        }}
        
        /* 目录部分不分页 */
        h2#_1,
        h2[id*="目录"],
        h2[id*="toc"] {{
            page-break-before: auto;
        }}
        
        h3 {{
            font-size: 16pt;
            color: #34495e;
            margin-top: 20px;
            page-break-after: avoid;
        }}
        
        h4 {{
            font-size: 14pt;
            color: #555;
            margin-top: 15px;
            page-break-after: avoid;
        }}
        
        h5 {{
            font-size: 12pt;
            color: #666;
            margin-top: 12px;
            page-break-after: avoid;
        }}
        
        p {{
            margin: 10px 0;
            text-align: justify;
        }}
        
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: "Consolas", "Monaco", "Courier New", monospace;
            font-size: 11pt;
            color: #c7254e;
        }}
        
        pre {{
            background-color: #f8f8f8;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            overflow-x: auto;
            page-break-inside: avoid;
            margin: 15px 0;
        }}
        
        pre code {{
            background-color: transparent;
            padding: 0;
            color: inherit;
            font-size: 10pt;
        }}
        
        ul, ol {{
            margin: 10px 0;
            padding-left: 30px;
        }}
        
        li {{
            margin: 5px 0;
        }}
        
        blockquote {{
            border-left: 4px solid #3498db;
            padding-left: 15px;
            margin: 15px 0;
            color: #555;
            font-style: italic;
            background-color: #f9f9f9;
            padding: 10px 15px;
        }}
        
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 15px 0;
            page-break-inside: avoid;
        }}
        
        th, td {{
            border: 1px solid #ddd;
            padding: 10px;
            text-align: left;
        }}
        
        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }}
        
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        
        /* 链接样式 */
        a {{
            color: #3498db;
            text-decoration: none;
        }}
        
        /* HTTP/HTTPS链接 - 蓝色+下划线，非常直观 */
        a[href^="http://"],
        a[href^="https://"] {{
            color: #0066cc;
            text-decoration: underline;
            font-weight: normal;
        }}
        
        /* 内部锚点链接 - 不显示下划线，避免干扰 */
        a[href^="#"] {{
            color: #333;
            text-decoration: none;
        }}
        
        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 15px auto;
        }}
        
        hr {{
            border: none;
            border-top: 2px solid #bdc3c7;
            margin: 30px 0;
        }}
        
        /* 代码高亮样式 */
        .codehilite {{ background: #f8f8f8; padding: 15px; border-radius: 5px; }}
        .codehilite .hll {{ background-color: #ffffcc }}
        .codehilite .c {{ color: #8f5902; font-style: italic }} /* Comment */
        .codehilite .k {{ color: #204a87; font-weight: bold }} /* Keyword */
        .codehilite .o {{ color: #ce5c00; font-weight: bold }} /* Operator */
        .codehilite .n {{ color: #000000 }} /* Name */
        .codehilite .s {{ color: #4e9a06 }} /* String */
        .codehilite .nb {{ color: #204a87 }} /* Name.Builtin */
        .codehilite .nf {{ color: #000000 }} /* Name.Function */
    </style>
</head>
<body>
{content}
</body>
</html>"""


def convert_urls_to_links(html_content):
    """
    将HTML中的纯文本URL转换为可点击的链接
    """
    import re
    
    # URL正则表达式
    url_pattern = r'(?<!href=")(?<!src=")(https?://[^\s<>"]+)'
    
    def replace_url(match):
        url = match.group(0)
        # 移除末尾的标点符号
        url = url.rstrip('.,;:!?)')
        return f'<a href="{url}">{url}</a>'
    
    # 只在<p>、<li>等标签内替换，避免影响已有的<a>标签
    def replace_in_tag(match):
        tag_content = match.group(0)
        # 如果已经包含<a>标签，跳过
        if '<a ' in tag_content:
            return tag_content
        return re.sub(url_pattern, replace_url, tag_content)
    
    # 在段落和列表项中替换URL
    html_content = re.sub(r'<p>.*?</p>', replace_in_tag, html_content, flags=re.DOTALL)
    html_content = re.sub(r'<li>.*?</li>', replace_in_tag, html_content, flags=re.DOTALL)
    html_content = re.sub(r'<td>.*?</td>', replace_in_tag, html_content, flags=re.DOTALL)
    
    return html_content


def fix_anchor_links(html_content, md_content):
    """
    修复HTML中的锚点链接，确保目录链接能正确跳转
    通过在每个标题前添加额外的锚点来实现
    """
    import re
    
    # 从markdown中提取所有标题
    md_heading_pattern = r'^(#{2,5})\s+(.+)$'
    md_headings = re.findall(md_heading_pattern, md_content, re.MULTILINE)
    
    # 生成标题到锚点的映射
    title_to_anchor = {}
    for hashes, title in md_headings:
        level = len(hashes)
        clean_title = title.strip()
        
        # 生成目录中使用的锚点格式（与generate_toc.py一致）
        anchor = clean_title.lower()
        anchor = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', anchor)
        anchor = re.sub(r'\s+', '-', anchor)
        anchor = anchor.strip('-')
        
        title_to_anchor[clean_title] = anchor
    
    # 在HTML中的每个标题前添加额外的锚点
    def add_anchor(match):
        full_tag = match.group(0)
        level = match.group(1)
        html_id = match.group(2)
        title_html = match.group(3)
        
        # 清理标题文本（移除HTML标签）
        clean_title = re.sub(r'<[^>]+>', '', title_html).strip()
        
        # 查找对应的锚点
        if clean_title in title_to_anchor:
            toc_anchor = title_to_anchor[clean_title]
            # 在标题前添加一个隐藏的锚点
            return f'<a id="{toc_anchor}" style="position:absolute;"></a>{full_tag}'
        
        return full_tag
    
    # 为所有标题添加额外的锚点
    heading_pattern = r'<h([2-5])[^>]*id="([^"]+)"[^>]*>(.+?)</h\1>'
    html_content = re.sub(heading_pattern, add_anchor, html_content, flags=re.DOTALL)
    
    return html_content


def convert_md_to_pdf(input_file, output_file=None):
    """
    将Markdown转换为PDF
    """
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"❌ 错误：找不到文件 {input_file}")
        return False
    
    # 生成输出文件名
    if output_file is None:
        output_file = os.path.splitext(input_file)[0] + '.pdf'
    
    print(f"📄 正在转换: {input_file} -> {output_file}")
    
    try:
        import markdown
        from markdown.extensions.codehilite import CodeHiliteExtension
        from markdown.extensions.fenced_code import FencedCodeExtension
        from markdown.extensions.tables import TableExtension
        from markdown.extensions.toc import TocExtension
        import weasyprint
        
        # 读取Markdown文件
        with open(input_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # 配置Markdown扩展
        extensions = [
            'extra',  # 包含tables, fenced_code等
            'codehilite',  # 代码高亮
            'toc',  # 目录
            'nl2br',  # 换行转<br>
        ]
        
        extension_configs = {
            'codehilite': {
                'css_class': 'codehilite',
                'linenums': False,
            },
            'toc': {
                'toc_depth': '2-4',
            }
        }
        
        # 转换Markdown为HTML
        md = markdown.Markdown(extensions=extensions, extension_configs=extension_configs)
        html_content = md.convert(md_content)
        
        # 将纯文本URL转换为链接
        html_content = convert_urls_to_links(html_content)
        
        # 修复锚点链接（传入原始markdown内容）
        html_content = fix_anchor_links(html_content, md_content)
        
        # 使用模板
        full_html = get_html_template(html_content)
        
        # 转换HTML为PDF
        weasyprint.HTML(string=full_html, base_url=os.path.dirname(os.path.abspath(input_file))).write_pdf(output_file)
        
        print(f"✅ 转换成功: {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ 转换失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    if '--help' in sys.argv or '-h' in sys.argv:
        print("""
用法：
  python3 md_to_pdf.py [输入文件] [输出文件]
  
选项：
  --help, -h       显示帮助
  --check          检查依赖是否安装
  
示例：
  python3 md_to_pdf.py 集群任务规划.md              # 转换为同名PDF
  python3 md_to_pdf.py input.md output.pdf        # 指定输出文件名
  python3 md_to_pdf.py --check                    # 检查依赖

依赖安装：
  pip install markdown weasyprint pygments
        """)
        return
    
    if '--check' in sys.argv:
        if check_dependencies():
            print("✅ 所有依赖已安装")
        else:
            sys.exit(1)
        return
    
    # 获取文件路径
    if len(sys.argv) > 1 and not sys.argv[1].startswith('--'):
        input_file = sys.argv[1]
    else:
        input_file = '集群任务规划.md'
    
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 转换
    success = convert_md_to_pdf(input_file, output_file)
    
    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main()
