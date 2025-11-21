# Markdown 工具集

这个文件夹包含用于处理 Markdown 文档的实用工具。

## 工具列表

### 1. generate_toc.py - 自动生成目录

自动扫描 Markdown 文档中的标题并生成目录。

**功能特点：**
- ✅ 自动识别 ##、###、####、##### 标题
- ✅ 生成符合 GitHub 规范的锚点链接
- ✅ 支持中文标题
- ✅ 自动缩进
- ✅ 保护代码块内容

**使用方法：**

```bash
# 更新默认文件（集群任务规划.md）
python3 utils/generate_toc.py

# 更新指定文件
python3 utils/generate_toc.py 文件名.md

# 预览模式（不修改文件）
python3 utils/generate_toc.py --preview
python3 utils/generate_toc.py -p

# 查看帮助
python3 utils/generate_toc.py --help
```

**示例输出：**
```
✓ 已更新现有目录（第10行）
✓ 目录已更新，文件已保存到: 集群任务规划.md
  共处理 48 个标题

标题统计：
  ## 标题: 6 个
  ### 标题: 7 个
  #### 标题: 9 个
  ##### 标题: 26 个
```

---

### 2. fix_punctuation.py - 统一标点符号

将 Markdown 文档中的英文标点符号转换为中文标点符号。

**功能特点：**
- ✅ 英文逗号 `,` → 中文逗号 `，`
- ✅ 中文句尾英文句号 `.` → 中文句号 `。`
- ✅ 保护代码块、链接、图片路径
- ✅ 保护纯英文内容
- ✅ 智能识别上下文

**使用方法：**

```bash
# 处理默认文件（集群任务规划.md）
python3 utils/fix_punctuation.py

# 处理指定文件
python3 utils/fix_punctuation.py 文件名.md

# 查看帮助
python3 utils/fix_punctuation.py --help
```

**示例输出：**
```
✓ 标点符号已统一，文件已保存到: 集群任务规划.md

统计信息:
  英文逗号: 115 → 40
  中文逗号: 362
  英文句号: 181 → 166
  中文句号: 272
```

---

## 快速开始

**方式一：自动安装（推荐）**
```bash
# format_md.sh 会自动检查并安装依赖
bash utils/format_md.sh 你的文件.md
```

**方式二：手动安装**
```bash
# 使用安装脚本
bash utils/install_deps.sh

# 或者使用pip
pip install -r utils/requirements.txt

# 然后处理文档
bash utils/format_md.sh 你的文件.md
```

**单独使用：**
```bash
# 只修复标点符号
python3 utils/fix_punctuation.py 文件.md

# 只生成目录
python3 utils/generate_toc.py 文件.md

# 只转换PDF
python3 utils/md_to_pdf.py 文件.md
```

---

## 工作流程建议

推荐的文档处理流程：

1. **编辑文档** - 正常编写/修改 Markdown 内容
2. **统一标点** - 运行 `fix_punctuation.py` 统一标点符号
3. **更新目录** - 运行 `generate_toc.py` 更新目录
4. **转换PDF** - 运行 `md_to_pdf.py` 生成PDF文档
5. **提交代码** - 提交到版本控制系统

或者直接使用 `format_md.sh` 一键完成所有步骤！

---

### 3. auto_divide.py - 自动添加分页符

在一级和二级标题前自动添加分页符，用于 Typora 等编辑器导出 PDF 时控制分页。

**功能特点：**
- ✅ 在 `#` 和 `##` 标题前添加分页符
- ✅ 智能检测，避免重复添加
- ✅ 保持文档开头第一个标题不分页
- ✅ 兼容 Typora、VS Code 等编辑器

**使用方法：**

```bash
# 处理默认文件（集群任务规划.md）
python3 utils/auto_divide.py

# 处理指定文件（直接修改原文件）
python3 utils/auto_divide.py 文件名.md

# 输出到新文件
python3 utils/auto_divide.py input.md output.md

# 查看帮助
python3 utils/auto_divide.py --help
```

**示例输出：**
```
📄 正在处理: 集群任务规划.md
✅ 处理完成: 集群任务规划.md
```

**添加的分页符格式：**
```html
<div style="page-break-after: always;"></div>
```

---

### 4. md_to_pdf.py - Markdown转PDF

将Markdown文件转换为PDF，支持中文、代码高亮、表格等。

**功能特点：**
- ✅ 纯Python实现，无需系统依赖
- ✅ 支持中文字体
- ✅ 代码语法高亮
- ✅ 支持表格、图片、链接
- ✅ 自动生成目录
- ✅ 美观的PDF样式
- ✅ 二级标题（##）自动分页
- ✅ HTTP/HTTPS链接可点击
- ✅ 自动添加页码

**使用方法：**

```bash
# 首次使用需要安装依赖
pip install -r utils/requirements.txt
# 或者
pip install markdown weasyprint pygments

# 转换默认文件
python3 utils/md_to_pdf.py

# 转换指定文件
python3 utils/md_to_pdf.py 文件名.md

# 指定输出文件名
python3 utils/md_to_pdf.py input.md output.pdf

# 检查依赖是否安装
python3 utils/md_to_pdf.py --check

# 查看帮助
python3 utils/md_to_pdf.py --help
```

**示例输出：**
```
📄 正在转换: 集群任务规划.md -> 集群任务规划.pdf
✅ 转换成功: 集群任务规划.pdf
```

---

### 5. prompt.py - 文档写作风格指南

提供标准化的写作风格提示词，帮助AI助手按照统一的风格继续撰写技术文档。

**功能特点：**
- ✅ 详细的写作风格规范
- ✅ 包含语言风格、结构组织、技术呈现等多个维度
- ✅ 提供实际应用示例和常用表达模板
- ✅ 可直接作为AI助手的系统提示词

**使用方法：**

```bash
# 查看完整的写作风格指南
python3 utils/prompt.py

# 在Python代码中使用
from utils.prompt import get_prompt
style_guide = get_prompt()
```

**主要内容：**
- 整体定位与目标读者
- 语言风格特征（口语化与学术性的平衡）
- 结构组织原则
- 技术内容呈现方式
- 代码与公式规范
- 特色写作技巧
- AI助手使用指南

---

### 6. format_md.sh - 一键处理脚本

自动执行完整的文档处理流程：统一标点符号 → 更新目录 → 添加分页符 → 可选转换PDF

**使用方法：**

```bash
# 处理默认文件（不转PDF）
bash utils/format_md.sh

# 处理指定文件（不转PDF）
bash utils/format_md.sh 文件名.md

# 处理默认文件并转PDF
bash utils/format_md.sh -pdf

# 处理指定文件并转PDF
bash utils/format_md.sh 文件名.md -pdf

# 或者
bash utils/format_md.sh -pdf 文件名.md
```

**处理流程：**
1. 统一标点符号（fix_punctuation.py）
2. 更新目录（generate_toc.py）
3. 添加分页符（auto_divide.py）
4. 转换PDF（md_to_pdf.py，仅当使用 `-pdf` 参数时）

---

## 依赖

**基础工具（fix_punctuation.py, generate_toc.py）：**
- Python 3.6+
- 标准库：`re`, `sys`, `os`

**分页符工具（auto_divide.py）：**
- Python 3.6+
- 标准库：`re`, `sys`, `os`

**PDF转换工具（md_to_pdf.py）：**
- Python 3.6+
- markdown>=3.4.0
- weasyprint>=60.0
- pygments>=2.16.0

安装PDF转换依赖：
```bash
pip install -r utils/requirements.txt
```

---

## 注意事项

1. **备份重要文件** - 虽然工具经过测试，但建议先备份重要文档
2. **版本控制** - 使用 Git 等版本控制系统可以轻松回滚更改
3. **预览模式** - 不确定效果时，先使用 `--preview` 参数预览
4. **编码格式** - 确保文件使用 UTF-8 编码

---

## 常见问题

**Q: 目录没有更新？**  
A: 确保文档中有 `## 目录` 标记，或者脚本会自动插入新目录。

**Q: 标点符号转换错误？**  
A: 检查是否是纯英文内容（会被自动跳过），或者在代码块中（会被保护）。

**Q: 支持其他 Markdown 文件吗？**  
A: 支持！只需指定文件名作为参数即可。

---

## 贡献

欢迎提出改进建议或报告问题！
