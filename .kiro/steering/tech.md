# Tech Stack

## Languages
- **Markdown**: Primary documentation format
- **Python 3.6+**: Utility scripts for document processing
- **LaTeX**: Academic paper writing (IEEEtran style)
- **Lisp/PDDL**: Task planning examples and code snippets

## Python Dependencies
```
markdown>=3.4.0
weasyprint>=60.0
pygments>=2.16.0
cffi>=1.15.0
pycparser>=2.21
opencc-python-reimplemented>=0.1.7
```

## Document Processing Tools (utils/)
| Tool | Purpose |
|------|---------|
| `generate_toc.py` | Auto-generate table of contents |
| `fix_punctuation.py` | Normalize Chinese/English punctuation |
| `add_paragraph_indent.py` | Add full-width space indentation |
| `auto_divide.py` | Insert page breaks before headings |
| `md_to_pdf.py` | Convert Markdown to PDF |
| `traditional_to_simplified.py` | Convert Traditional to Simplified Chinese |
| `format_md.sh` | One-click document formatting pipeline |

## Common Commands

### Document Formatting
```bash
# Full formatting pipeline (no PDF)
bash utils/format_md.sh 文件名.md

# Full formatting pipeline with PDF export
bash utils/format_md.sh 文件名.md -pdf

# Individual tools
python3 utils/generate_toc.py 文件名.md
python3 utils/fix_punctuation.py 文件名.md
python3 utils/add_paragraph_indent.py 文件名.md
python3 utils/md_to_pdf.py 文件名.md
```

### Install Dependencies
```bash
pip install -r utils/requirements.txt
```

## LaTeX Structure (docs/essay-gsi/)
- `main.tex`: Entry point
- `main.bib`: Bibliography
- `mytemplate.cls`: Custom document class
- `chapter/`: Chapter files (intro, problem, experiments, appendix)
- `fig/`: Figures and diagrams
