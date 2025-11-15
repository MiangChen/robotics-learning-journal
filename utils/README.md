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

## 工作流程建议

推荐的文档处理流程：

1. **编辑文档** - 正常编写/修改 Markdown 内容
2. **统一标点** - 运行 `fix_punctuation.py` 统一标点符号
3. **更新目录** - 运行 `generate_toc.py` 更新目录
4. **提交代码** - 提交到版本控制系统

可以创建一个简单的脚本自动化这个流程：

```bash
#!/bin/bash
# format_md.sh

echo "正在统一标点符号..."
python3 utils/fix_punctuation.py 集群任务规划.md

echo "正在更新目录..."
python3 utils/generate_toc.py 集群任务规划.md

echo "✓ 文档格式化完成！"
```

---

## 依赖

这些工具只使用 Python 标准库，无需安装额外依赖：
- Python 3.6+
- 标准库：`re`, `sys`, `os`

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
