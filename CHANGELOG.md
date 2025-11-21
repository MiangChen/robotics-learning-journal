# 更新日志

## 2024-11-21

### 新增功能

#### 1. Git Submodule 集成
- 将私密文档仓库 `PersonalDocument` 作为子模块添加到 `docs/` 目录
- 实现公开代码与私密文档的分离管理
- 添加详细的子模块使用指南（SETUP_SUBMODULE.md 和 QUICK_START.md）

#### 2. 繁体字转简体字工具
- 新增 `traditional_to_simplified.py` 工具
- 智能保护代码块、链接、图片等特殊内容
- 提供预览模式和准确的转换统计
- 集成到 `format_md.sh` 工作流中作为第一步

#### 3. 文档写作风格指南
- 新增 `prompt.py` 包含详细的写作风格规范
- 可作为 AI 助手的系统提示词
- 包含实际应用示例和常用表达模板

#### 4. 自动分页符工具
- 新增 `auto_divide.py` 在一级和二级标题前添加分页符
- 智能检测避免重复添加
- 兼容 Typora 等编辑器的 PDF 导出

### 优化改进

#### format_md.sh 工作流
更新处理流程为：
1. 繁体字转简体字 ✨ 新增
2. 统一标点符号
3. 更新目录
4. 添加分页符 ✨ 新增
5. 转换 PDF（可选，需要 `-pdf` 参数）

#### md_to_pdf.py
- 移除 CSS 中的自动分页规则
- 分页完全由 Markdown 中的 `<div>` 标签控制
- 优化代码结构和错误处理

### 文档更新

- 更新 README.md 添加子模块使用说明
- 更新 utils/README.md 添加所有新工具的文档
- 新增 SETUP_SUBMODULE.md 详细的子模块设置指南
- 新增 QUICK_START.md 快速开始指南
- 新增 TRADITIONAL_TO_SIMPLIFIED_GUIDE.md 繁简转换工具指南

### 依赖更新

requirements.txt 新增：
- `opencc-python-reimplemented>=0.1.7` - 繁简转换

### 目录结构变化

```
robotics-learning-journal/
├── docs/                    # 新增：私密子模块
│   ├── 集群任务规划.md
│   ├── 集群任务规划.pdf
│   └── asset/
├── utils/
│   ├── traditional_to_simplified.py  # 新增
│   ├── auto_divide.py               # 新增
│   ├── prompt.py                    # 新增
│   ├── format_md.sh                 # 更新
│   ├── md_to_pdf.py                 # 优化
│   └── ...
├── .gitignore               # 新增
├── .gitmodules              # 新增
├── SETUP_SUBMODULE.md       # 新增
├── QUICK_START.md           # 新增
└── CHANGELOG.md             # 新增
```

## 使用示例

### 完整工作流

```bash
# 处理文档（繁简转换 + 格式化）
bash utils/format_md.sh docs/集群任务规划.md

# 处理文档并生成 PDF
bash utils/format_md.sh docs/集群任务规划.md -pdf
```

### 单独使用工具

```bash
# 繁体转简体
python3 utils/traditional_to_simplified.py docs/文档.md

# 添加分页符
python3 utils/auto_divide.py docs/文档.md

# 查看写作风格指南
python3 utils/prompt.py
```

### 子模块操作

```bash
# 克隆仓库（包含子模块）
git clone --recursive git@github.com:MiangChen/robotics-learning-journal.git

# 更新子模块
git submodule update --remote docs

# 在子模块中提交更改
cd docs
git add .
git commit -m "Update document"
git push
cd ..
git add docs
git commit -m "Update docs submodule"
git push
```

## 已知问题

无

## 计划功能

- [ ] 支持批量处理多个文档
- [ ] 添加文档质量检查工具
- [ ] 支持自定义分页规则
- [ ] 添加文档统计分析功能
