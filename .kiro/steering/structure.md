# Project Structure

```
robotics-learning-journal/
├── README.md                    # Project overview and navigation
├── VLA入门理解.md               # VLA introduction (RT-1, RT-2, OpenVLA)
├── 任务规划.pdf                 # Compiled task planning notes
├── legged_gym解读.md            # Legged robot gym analysis
├── 脑科学启发论文.md            # Brain-inspired research notes
├── 论文写作规范.md              # Academic writing guidelines
├── 直观体会.md                  # Intuitive understanding notes
├── LLM RL Papers.md             # LLM + RL research papers
│
├── docs/                        # Extended documentation
│   ├── 任务规划.md              # Main task planning document (2500+ lines)
│   ├── 研究方向.md              # Research directions
│   ├── workflow_essay.md        # Essay workflow
│   ├── prompt.py                # Writing style guide for AI assistants
│   │
│   ├── essay-gsi/               # LaTeX academic paper
│   │   ├── main.tex             # Main LaTeX file
│   │   ├── main.bib             # Bibliography
│   │   ├── mytemplate.cls       # Custom template
│   │   ├── chapter/             # Chapter files
│   │   └── fig/                 # Figures
│   │
│   └── asset/                   # Documentation assets
│       └── 任务规划.asset/      # Images for task planning doc
│
├── utils/                       # Document processing utilities
│   ├── README.md                # Utility documentation
│   ├── requirements.txt         # Python dependencies
│   ├── format_md.sh             # One-click formatting script
│   ├── generate_toc.py          # TOC generator
│   ├── fix_punctuation.py       # Punctuation normalizer
│   ├── add_paragraph_indent.py  # Paragraph indentation
│   ├── auto_divide.py           # Page break inserter
│   ├── md_to_pdf.py             # PDF converter
│   └── traditional_to_simplified.py  # Chinese converter
│
├── asset/                       # Root-level assets
│   └── *.png                    # Images for root docs
│
├── pdf/                         # Reference papers (PDF)
│   └── *.pdf                    # Multi-robot task allocation papers
│
└── .kiro/                       # Kiro configuration
    └── steering/                # AI assistant guidelines
```

## Key Conventions

### Documentation Files
- Main docs at root level for quick access
- Extended/detailed docs in `docs/`
- Assets stored alongside their documents in `asset/` folders

### Naming Conventions
- Chinese filenames for Chinese content
- Use full-width spaces (　) for paragraph indentation
- Page breaks: `<div style="page-break-after: always;"></div>`

### Document Hierarchy
- `#` - Major sections (rarely used)
- `##` - Main chapters
- `###` - Subsections
- `####` - Topics/Cases
- `#####` - Paper titles

### Asset Organization
- `asset/文档名.asset/` - Images specific to a document
- Root `asset/` - Shared images
