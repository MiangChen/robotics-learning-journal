# 繁体字转简体字工具使用指南

## 功能说明

`traditional_to_simplified.py` 是一个智能的繁体字转简体字工具，专为Markdown文档设计。

### 核心特性

1. **智能转换**：自动识别并转换繁体字为简体字
2. **内容保护**：保护特殊内容不被转换
   - 代码块（```...```）
   - 行内代码（`...`）
   - 链接（[text](url)）
   - 图片（![alt](url)）
   - HTML标签（<div>...</div>）
3. **预览模式**：转换前可以预览效果
4. **统计信息**：显示转换的繁体字数量

## 安装依赖

```bash
pip install opencc-python-reimplemented
```

或者使用 requirements.txt：

```bash
pip install -r utils/requirements.txt
```

## 使用方法

### 1. 基本用法

```bash
# 直接修改原文件
python3 utils/traditional_to_simplified.py 文档.md

# 输出到新文件
python3 utils/traditional_to_simplified.py input.md output.md
```

### 2. 预览模式

在实际转换前，先预览效果：

```bash
python3 utils/traditional_to_simplified.py 文档.md --preview
```

输出示例：
```
📄 正在处理: 文档.md

==================================================
预览模式 - 显示前500个字符
==================================================
# 测试文档

这是一个包含简体字的测试文档...
==================================================

✓ 检测到 156 个繁体字被转换
  示例: 機 學 習 強 化 測 試 執 行 規 劃
```

### 3. 检查依赖

```bash
python3 utils/traditional_to_simplified.py --check
```

### 4. 查看帮助

```bash
python3 utils/traditional_to_simplified.py --help
```

## 转换示例

### 输入（繁体字）

```markdown
# 機器學習

這是一個關於機器學習的文檔。

## 深度學習

深度學習是機器學習的一個分支。

### 代碼示例

```python
# 這裡的繁體字會被保護
def 測試函數():
    print("這是代碼")
```

行內代碼：`這是行內代碼`

[這是鏈接](https://example.com/測試)
```

### 输出（简体字）

```markdown
# 机器学习

这是一个关于机器学习的文档。

## 深度学习

深度学习是机器学习的一个分支。

### 代码示例

```python
# 這裡的繁體字會被保護
def 測試函數():
    print("這是代碼")
```

行内代码：`這是行內代碼`

[這是鏈接](https://example.com/測試)
```

**注意**：代码块、行内代码、链接中的繁体字被保护，不会转换。

## 保护机制说明

### 被保护的内容

1. **代码块**
   ```python
   # 這裡的內容不會被轉換
   ```

2. **行内代码**
   `這裡的內容不會被轉換`

3. **链接文本和URL**
   [這裡不轉換](https://example.com/這裡也不轉換)

4. **图片alt和路径**
   ![這裡不轉換](asset/這裡也不轉換.png)

5. **HTML标签**
   <div style="這裡不轉換">內容會轉換</div>

### 为什么需要保护？

- **代码**：代码中的变量名、注释可能是有意使用繁体字
- **链接**：URL路径转换可能导致链接失效
- **图片**：文件路径转换会导致图片无法显示

## 常见问题

### Q: 如何批量处理多个文件？

A: 可以使用shell脚本：

```bash
for file in docs/*.md; do
    python3 utils/traditional_to_simplified.py "$file"
done
```

### Q: 转换后如何恢复？

A: 建议使用Git版本控制：

```bash
# 转换前先提交
git add .
git commit -m "Before traditional to simplified conversion"

# 转换
python3 utils/traditional_to_simplified.py 文档.md

# 如果需要恢复
git checkout 文档.md
```

### Q: 可以只转换部分内容吗？

A: 目前不支持。建议：
1. 使用预览模式查看效果
2. 输出到新文件，手动合并需要的部分

### Q: 转换速度如何？

A: 对于普通文档（<1MB），转换通常在1秒内完成。

## 技术细节

### 使用的转换库

- **OpenCC**（Open Chinese Convert）
- 转换配置：`t2s`（Traditional to Simplified）
- 支持的转换：
  - 繁体中文 → 简体中文
  - 台湾正体 → 大陆简体
  - 香港繁体 → 大陆简体

### 正则表达式保护

工具使用正则表达式识别需要保护的内容：

- 代码块：`r'```[^\n]*\n[\s\S]*?```'`
- 行内代码：`r'`[^`\n]+`'`
- 链接：`r'\[([^\]]+)\]\(([^\)]+)\)'`
- 图片：`r'!\[([^\]]*)\]\(([^\)]+)\)'`
- HTML：`r'<[^>]+>'`

## 集成到工作流

可以将繁体转简体集成到文档处理流程中：

```bash
# 1. 转换繁体为简体
python3 utils/traditional_to_simplified.py docs/文档.md

# 2. 格式化文档
bash utils/format_md.sh docs/文档.md

# 3. 生成PDF
bash utils/format_md.sh docs/文档.md -pdf
```

## 贡献

如果发现转换问题或有改进建议，欢迎提Issue或PR！
