#!/usr/bin/env python3
"""Render the two repository guides using a small supported Markdown subset."""
import argparse
import html
from pathlib import Path
import re
import tempfile

import fitz

ROOT = Path(__file__).resolve().parents[1]


def inline(value):
    # Protect code and links while escaping all source text.
    pieces = []
    token = re.compile(r'(`[^`]+`|\[[^\]]+\]\(https?://[^)]+\)|\*\*[^*]+\*\*)')
    for part in token.split(value):
        if part.startswith('`') and part.endswith('`'):
            pieces.append('<code>'+html.escape(part[1:-1])+'</code>')
        elif part.startswith('**') and part.endswith('**'):
            pieces.append('<strong>'+html.escape(part[2:-2])+'</strong>')
        elif (match := re.fullmatch(r'\[([^\]]+)\]\((https?://[^)]+)\)', part)):
            pieces.append('<a href="'+html.escape(match[2], quote=True)+'">'+html.escape(match[1])+'</a>')
        else:
            pieces.append(html.escape(part))
    return ''.join(pieces)


def convert(markdown):
    lines = markdown.strip().splitlines()
    out, i = [], 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
        elif line.startswith('```'):
            block = []
            i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                block.append(lines[i])
                i += 1
            i += 1
            out.append('<pre>'+html.escape('\n'.join(block))+'</pre>')
        elif line.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                cells = [x.strip() for x in lines[i].strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?', c) for c in cells):
                    tag = 'th' if not rows else 'td'
                    rows.append('<tr>'+''.join(f'<{tag}>'+inline(c)+f'</{tag}>' for c in cells)+'</tr>')
                i += 1
            out.append('<table>'+''.join(rows)+'</table>')
        elif (match := re.match(r'^(#{1,3}) (.+)', line)):
            level = len(match[1])
            out.append(f'<h{level}>'+inline(match[2])+f'</h{level}>')
            i += 1
        elif line.startswith('> '):
            out.append('<blockquote>'+inline(line[2:])+'</blockquote>')
            i += 1
        elif line.startswith('- '):
            items = []
            while i < len(lines) and lines[i].startswith('- '):
                items.append('<li>'+inline(lines[i][2:])+'</li>')
                i += 1
            out.append('<ul>'+''.join(items)+'</ul>')
        elif re.match(r'^\d+\. ', line):
            items = []
            while i < len(lines) and re.match(r'^\d+\. ', lines[i]):
                items.append('<li>'+inline(re.sub(r'^\d+\. ', '', lines[i]))+'</li>')
                i += 1
            out.append('<ol>'+''.join(items)+'</ol>')
        else:
            paragraph = [line]
            i += 1
            while i < len(lines) and lines[i].strip() and not re.match(r'^(#|\||```|> |- |\d+\. )', lines[i]):
                paragraph.append(lines[i])
                i += 1
            out.append('<p>'+inline(' '.join(paragraph))+'</p>')
    return '<html><body>'+''.join(out)+'</body></html>'


def build(source, output, font, bold_font):
    markdown = source.read_text()
    parts = markdown.split('<!-- pagebreak -->')
    css = '''
    @font-face {font-family: Body; src: url(regular.ttf);}
    @font-face {font-family: Body; src: url(bold.ttf); font-weight: bold;}
    body {font-family: Body; font-size: 10.2pt; line-height: 1.6; color: #223247;}
    h1 {font-size: 28pt; color: #11243b; margin-top: 42pt; margin-bottom: 18pt;}
    h2 {font-size: 19pt; line-height: 1.35; color: #133b57; margin-top: 7pt; margin-bottom: 17pt;}
    h3 {font-size: 12pt; color: #176b71; margin-top: 16pt; margin-bottom: 7pt;}
    p {margin-top: 0; margin-bottom: 10pt;}
    table {width: 100%; border-collapse: collapse; margin-top: 8pt; margin-bottom: 15pt; font-size: 9pt;}
    th {background-color: #e4edf3; color: #123c58; text-align: left;}
    th, td {border: 0.5pt solid #c7d3dc; padding: 7pt; vertical-align: top;}
    pre {font-family: monospace; font-size: 8.4pt; line-height: 1.5; white-space: pre-wrap;
         background-color: #eef3f7; padding: 10pt; margin-bottom: 13pt;}
    code {font-family: monospace; font-size: 9pt; color: #12546b;}
    blockquote {background-color: #eaf4f1; border-left: 3pt solid #238681; padding: 12pt; margin: 9pt 0 15pt 0;}
    li {margin-bottom: 5pt;}
    ul, ol {padding-left: 20pt; margin-bottom: 12pt;}
    a {color: #146f95; text-decoration: underline;}
    '''
    with tempfile.TemporaryDirectory() as temporary:
        temp = Path(temporary)
        fallback = None if font else fitz.Font('korea').buffer
        (temp/'regular.ttf').write_bytes(Path(font).read_bytes() if font else fallback)
        (temp/'bold.ttf').write_bytes(Path(bold_font).read_bytes() if bold_font else (Path(font).read_bytes() if font else fallback))
        writer = fitz.DocumentWriter(str(temp/'body.pdf'))
        toc = []
        page_count = 0
        for section in parts:
            heading = re.search(r'^#{1,2} (.+)', section, re.M)
            toc.append([1, heading[1] if heading else 'Guide', page_count+1])
            story = fitz.Story(convert(section), user_css=css, archive=fitz.Archive(str(temp)))

            def rectfn(number, filled):
                nonlocal page_count
                page_count += 1
                if number > 10:
                    raise RuntimeError('Section does not fit; inspect long tables/code')
                box = fitz.paper_rect('a4')
                return box, fitz.Rect(44, 51, box.width-44, box.height-51), None

            story.write(writer, rectfn)
        writer.close()
        doc = fitz.open(temp/'body.pdf')
        links = re.findall(r'\[([^\]]+)\]\((https?://[^)]+)\)', markdown)
        for i, page in enumerate(doc):
            page.draw_line((44, 33), (page.rect.width-44, 33), color=(0.13, 0.42, 0.48), width=1)
            page.insert_text((44, 25), 'CODEX HACKATHON PLAYBOOK  /  PREPARATION GUIDE', fontsize=7.5, color=(0.31, 0.39, 0.46))
            page.insert_text((44, page.rect.height-27), '2026-10-31  |  Public preparation material', fontsize=7.5, color=(0.31, 0.39, 0.46))
            page.insert_text((page.rect.width-85, page.rect.height-27), f'{i+1} / {len(doc)}', fontsize=8, color=(0.2, 0.3, 0.4))
            for label, url in links:
                for rectangle in page.search_for(label):
                    page.insert_link({'kind': fitz.LINK_URI, 'from': rectangle, 'uri': url})
        doc.set_toc(toc)
        doc.set_metadata({'title': toc[0][1], 'author': 'suwonyoo', 'subject': 'Korean hackathon preparation guide',
                          'keywords': 'Codex, preparation, evidence, Korean', 'creator': 'Codex Hackathon Playbook'})
        doc.subset_fonts()
        output.parent.mkdir(parents=True, exist_ok=True)
        doc.save(output, garbage=4, deflate=True)
        print(f'{output.name}: {len(doc)} pages, {output.stat().st_size} bytes')
        doc.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--font', help='Optional local Korean TTF; otherwise use bundled CJK font')
    parser.add_argument('--bold-font', help='Optional local bold Korean TTF')
    args = parser.parse_args()
    for source, target in [('codex-operations.md', '01-codex-operations-ko.pdf'),
                           ('explanation-preparation.md', '02-explanation-preparation-ko.pdf')]:
        build(ROOT/'docs/guides'/source, ROOT/'pdf'/target, args.font, args.bold_font)


if __name__ == '__main__':
    main()
