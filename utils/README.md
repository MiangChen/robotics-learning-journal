# Markdown 工具集

这个文件夹包含用于处理 Markdown 文档的实用工具。

## 工具列表

### 1. md_to_pdf_pandoc.py - Markdown 转 PDF

使用 Pandoc 将 Markdown 文件转换为 PDF，支持中文、代码高亮、图片、表格等。

**功能特点：**
- ✅ 基于 Pandoc，转换质量高
- ✅ 支持中文（XeLaTeX + CJK 字体）
- ✅ 自动生成目录
- ✅ 代码语法高亮
- ✅ 支持图片、表格、超链接
- ✅ 章节自动编号

**使用方法：**

```bash
# 转换指定文件（输出同名 PDF）
python3 utils/md_to_pdf_pandoc.py 文件名.md

# 指定输出文件名
python3 utils/md_to_pdf_pandoc.py input.md output.pdf
```

**依赖安装：**
```bash
sudo apt install pandoc texlive-xetex texlive-lang-chinese
```

---

### 2. fix_punctuation.py - 统一标点符号

将 Markdown 文档中的英文标点符号转换为中文标点符号。

**功能特点：**
- ✅ 英文逗号 `,` → 中文逗号 `，`
- ✅ 中文句尾英文句号 `.` → 中文句号 `。`
- ✅ 保护代码块、链接、图片路径
- ✅ 保护纯英文内容

**使用方法：**

```bash
python3 utils/fix_punctuation.py 文件名.md
```

---

### 3. format_md.sh - 一键格式化

自动执行文档格式化流程。

**使用方法：**

```bash
bash utils/format_md.sh 文件名.md
```

---

## Git 工具

- `push.sh` - 快速提交并推送
- `smart_pull.sh` - 智能拉取（处理 submodule）

---

## 依赖

**PDF 转换：**
```bash
sudo apt install pandoc texlive-xetex texlive-lang-chinese
```

**Python 工具：**
- Python 3.6+
- 标准库即可
