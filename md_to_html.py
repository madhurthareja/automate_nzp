#!/usr/bin/env python3
"""Simple Markdown -> HTML converter CLI.

Usage:
  python md_to_html.py input.md [-o output.html]

Tries to use the `markdown` package if available. If not, falls back to a small
safe converter that handles headings, paragraphs, fenced code blocks, bold,
italic and links.
"""
import argparse
import sys
import pathlib
import re


def fallback_md_to_html(text: str) -> str:
    """Very small markdown -> HTML fallback converter.

    - Converts #..###### headings
    - Handles fenced code blocks (```)
    - Converts **bold**, *italic* and [text](url)
    - Wraps paragraphs in <p>
    This is intentionally small and safe — for better output install `markdown`.
    """
    lines = text.splitlines()
    out_lines = []
    in_code = False
    code_buf = []

    def flush_paragraph(buf):
        if not buf:
            return []
        paragraph = "\n".join(buf).strip()
        if not paragraph:
            return []
        # inline replacements: links, bold, italic
        paragraph = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", paragraph)
        paragraph = re.sub(r"\*(.+?)\*", r"<em>\1</em>", paragraph)
        paragraph = re.sub(r"\[(.*?)\]\((.*?)\)", r"<a href=\"\2\">\1</a>", paragraph)
        return [f"<p>{paragraph}</p>"]

    para_buf = []
    for line in lines:
        if line.strip().startswith('```'):
            if in_code:
                # close code block
                out_lines.append('<pre><code>')
                out_lines.extend([escape_html(l) for l in code_buf])
                out_lines.append('</code></pre>')
                code_buf = []
                in_code = False
            else:
                # start code block
                in_code = True
            continue

        if in_code:
            code_buf.append(line)
            continue

        m = re.match(r'^(#{1,6})\s*(.*)$', line)
        if m:
            # flush paragraph before heading
            out_lines.extend(flush_paragraph(para_buf))
            para_buf = []
            level = len(m.group(1))
            heading = escape_html(m.group(2).strip())
            out_lines.append(f"<h{level}>{heading}</h{level}>")
            continue

        if not line.strip():
            out_lines.extend(flush_paragraph(para_buf))
            para_buf = []
            continue

        para_buf.append(line)

    # end loop
    out_lines.extend(flush_paragraph(para_buf))
    # if code block left open, close safely
    if in_code:
        out_lines.append('<pre><code>')
        out_lines.extend([escape_html(l) for l in code_buf])
        out_lines.append('</code></pre>')

    return '\n'.join(out_lines)


def escape_html(s: str) -> str:
    return (s.replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;'))


def convert_markdown(text: str) -> str:
    try:
        import markdown
        # Use some common extensions if available
        html = markdown.markdown(text, extensions=['fenced_code', 'tables', 'toc'])
        return html
    except Exception:
        # fallback
        return fallback_md_to_html(text)


def build_full_html(body_html: str, title: str = 'Document') -> str:
    return f"""<!doctype html>
<html lang=\"en\"> 
<head>
  <meta charset=\"utf-8\"> 
  <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"> 
  <title>{escape_html(title)}</title>
  <style>
    body {{ font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; max-width: 900px; margin: 32px auto; padding: 0 16px; line-height:1.6 }}
    pre {{ background:#f6f8fa; padding:12px; overflow:auto }}
    code {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, 'Roboto Mono', 'Segoe UI Mono' }}
    h1,h2,h3,h4 {{ margin-top:1.4em }}
    p {{ margin: 0.6em 0 }}
  </style>
</head>
<body>
{body_html}
</body>
</html>"""


def main(argv=None):
    parser = argparse.ArgumentParser(description='Convert a markdown file to HTML')
    parser.add_argument('input', help='Input markdown file')
    parser.add_argument('-o', '--output', help='Output HTML file (defaults to input.html)')
    parser.add_argument('--title', help='HTML title (defaults to input filename)')
    args = parser.parse_args(argv)

    inp = pathlib.Path(args.input)
    if not inp.exists():
        print(f"Input file not found: {inp}", file=sys.stderr)
        return 2

    text = inp.read_text(encoding='utf-8')
    body = convert_markdown(text)
    title = args.title if args.title else inp.stem
    html = build_full_html(body, title=title)

    out_path = pathlib.Path(args.output) if args.output else inp.with_suffix('.html')
    out_path.write_text(html, encoding='utf-8')
    print(f"Wrote: {out_path}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
