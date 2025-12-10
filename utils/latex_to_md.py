#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LaTeX to Markdown Converter
Converts LaTeX (.tex) files to Markdown (.md) format.

Usage:
    python3 utils/latex_to_md.py input.tex [output.md]
    python3 utils/latex_to_md.py docs/essay-gsi/simulation_paper_related_work.tex
"""

import re
import sys
import os


def latex_to_markdown(content: str) -> str:
    """Convert LaTeX content to Markdown."""
    
    # Remove LaTeX comments (lines starting with %)
    content = re.sub(r'^%.*$', '', content, flags=re.MULTILINE)
    
    # === Document Structure ===
    
    # \section{Title} -> ## Title
    content = re.sub(r'\\section\*?\{([^}]+)\}', r'## \1', content)
    
    # \subsection{Title} -> ### Title
    content = re.sub(r'\\subsection\*?\{([^}]+)\}', r'### \1', content)
    
    # \subsubsection{Title} -> #### Title
    content = re.sub(r'\\subsubsection\*?\{([^}]+)\}', r'#### \1', content)
    
    # \paragraph{Title} -> **Title**
    content = re.sub(r'\\paragraph\*?\{([^}]+)\}', r'**\1**', content)
    
    # === Text Formatting ===
    
    # \textbf{text} -> **text**
    content = re.sub(r'\\textbf\{([^}]+)\}', r'**\1**', content)
    
    # \textit{text} or \emph{text} -> *text*
    content = re.sub(r'\\textit\{([^}]+)\}', r'*\1*', content)
    content = re.sub(r'\\emph\{([^}]+)\}', r'*\1*', content)
    
    # \texttt{text} -> `text`
    content = re.sub(r'\\texttt\{([^}]+)\}', r'`\1`', content)
    
    # \underline{text} -> <u>text</u>
    content = re.sub(r'\\underline\{([^}]+)\}', r'<u>\1</u>', content)
    
    # === Citations and References ===
    
    # \cite{key} -> [key]
    content = re.sub(r'~?\\cite\{([^}]+)\}', r'[\1]', content)
    
    # \ref{label} -> [ref:label]
    content = re.sub(r'~?\\ref\{([^}]+)\}', r'[ref:\1]', content)
    
    # \label{...} -> remove
    content = re.sub(r'\\label\{[^}]+\}', '', content)
    
    # === Lists ===
    
    # \begin{itemize} ... \end{itemize}
    content = re.sub(r'\\begin\{itemize\}', '', content)
    content = re.sub(r'\\end\{itemize\}', '', content)
    
    # \begin{enumerate} ... \end{enumerate}
    content = re.sub(r'\\begin\{enumerate\}', '', content)
    content = re.sub(r'\\end\{enumerate\}', '', content)
    
    # \item -> - (for itemize) or 1. (simplified)
    content = re.sub(r'\\item\s*', '- ', content)
    
    # === Tables ===
    
    # Simple table conversion (basic support)
    def convert_table(match):
        table_content = match.group(1)
        rows = []
        for line in table_content.split('\\\\'):
            line = line.strip()
            if line and not line.startswith('\\') and '&' in line:
                cells = [cell.strip() for cell in line.split('&')]
                rows.append('| ' + ' | '.join(cells) + ' |')
        
        if len(rows) >= 1:
            # Add header separator after first row
            num_cols = rows[0].count('|') - 1
            separator = '|' + '---|' * num_cols
            rows.insert(1, separator)
        
        return '\n'.join(rows)
    
    content = re.sub(r'\\begin\{tabular\}\{[^}]*\}(.*?)\\end\{tabular\}', 
                     convert_table, content, flags=re.DOTALL)
    
    # Remove table environment wrappers
    content = re.sub(r'\\begin\{table\*?\}\[[^\]]*\]', '', content)
    content = re.sub(r'\\end\{table\*?\}', '', content)
    content = re.sub(r'\\centering', '', content)
    content = re.sub(r'\\caption\{([^}]+)\}', r'*Table: \1*', content)
    content = re.sub(r'\\toprule', '', content)
    content = re.sub(r'\\midrule', '', content)
    content = re.sub(r'\\bottomrule', '', content)
    
    # === Figures ===
    
    # \begin{figure} ... \end{figure}
    content = re.sub(r'\\begin\{figure\}\[[^\]]*\]', '', content)
    content = re.sub(r'\\end\{figure\}', '', content)
    
    # \includegraphics[...]{path} -> ![](path)
    content = re.sub(r'\\includegraphics\[[^\]]*\]\{([^}]+)\}', r'![](\1)', content)
    
    # === Code Listings ===
    
    def convert_listing(match):
        options = match.group(1) if match.group(1) else ''
        code = match.group(2)
        
        # Extract language from options
        lang_match = re.search(r'language=(\w+)', options)
        lang = lang_match.group(1).lower() if lang_match else ''
        
        return f'```{lang}\n{code.strip()}\n```'
    
    content = re.sub(r'\\begin\{lstlisting\}\[([^\]]*)\](.*?)\\end\{lstlisting\}',
                     convert_listing, content, flags=re.DOTALL)
    
    # === Math ===
    
    # Inline math: $...$ stays the same
    # Display math: \[ ... \] -> $$ ... $$
    content = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', content, flags=re.DOTALL)
    
    # \begin{equation} ... \end{equation} -> $$ ... $$
    content = re.sub(r'\\begin\{equation\*?\}(.*?)\\end\{equation\*?\}', 
                     r'$$\1$$', content, flags=re.DOTALL)
    
    # === Special Characters ===
    
    content = content.replace('\\&', '&')
    content = content.replace('\\%', '%')
    content = content.replace('\\$', '$')
    content = content.replace('\\#', '#')
    content = content.replace('\\textbackslash', '\\')
    content = content.replace('~', ' ')  # Non-breaking space
    content = content.replace('``', '"')
    content = content.replace("''", '"')
    content = content.replace('--', '–')
    content = content.replace('---', '—')
    
    # === Symbols ===
    
    content = content.replace('\\cmark', '✓')
    content = content.replace('\\xmark', '✗')
    content = content.replace('\\checkmark', '✓')
    content = content.replace('\\times', '×')
    content = content.replace('\\ldots', '...')
    content = content.replace('\\dots', '...')
    
    # === Remove remaining LaTeX commands ===
    
    # Remove \noindent
    content = re.sub(r'\\noindent\s*', '', content)
    
    # Remove \vspace, \hspace
    content = re.sub(r'\\[vh]space\*?\{[^}]*\}', '', content)
    
    # Remove \newline, \\
    content = re.sub(r'\\newline', '\n', content)
    content = re.sub(r'\\\\\s*', '\n', content)
    
    # Remove empty lines with only whitespace
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    
    # Clean up extra whitespace
    content = re.sub(r'[ \t]+', ' ', content)
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    return content.strip()


def convert_file(input_path: str, output_path: str = None) -> str:
    """Convert a LaTeX file to Markdown."""
    
    if not os.path.exists(input_path):
        print(f"Error: File not found: {input_path}")
        sys.exit(1)
    
    # Read input file
    with open(input_path, 'r', encoding='utf-8') as f:
        latex_content = f.read()
    
    # Convert
    md_content = latex_to_markdown(latex_content)
    
    # Determine output path
    if output_path is None:
        base = os.path.splitext(input_path)[0]
        output_path = base + '.md'
    
    # Write output file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"✓ Converted: {input_path} -> {output_path}")
    return output_path


def main():
    if len(sys.argv) < 2 or '--help' in sys.argv or '-h' in sys.argv:
        print("""
LaTeX to Markdown Converter

Usage:
    python3 latex_to_md.py <input.tex> [output.md]

Examples:
    python3 utils/latex_to_md.py docs/essay-gsi/simulation_paper_related_work.tex
    python3 utils/latex_to_md.py paper.tex paper.md

Supported conversions:
    - Sections (\\section, \\subsection, \\subsubsection)
    - Text formatting (\\textbf, \\textit, \\emph, \\texttt)
    - Lists (itemize, enumerate)
    - Tables (basic tabular)
    - Figures (\\includegraphics)
    - Citations (\\cite -> [key])
    - Math (inline $...$ and display $$...$$)
    - Code listings (lstlisting)
        """)
        return
    
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    convert_file(input_path, output_path)


if __name__ == '__main__':
    main()
