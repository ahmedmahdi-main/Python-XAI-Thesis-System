from pathlib import Path
p=Path('docs/complete_code_explanation/build_figure_book.py');s=p.read_text(encoding='utf8')
s=s.replace(" return md.renderer.render(tokens,md.options,{})", " rendered=md.renderer.render(tokens,md.options,{})\n return re.sub(r'(<h[1-6]>الأسطر )([0-9]+–[0-9]+)(</h[1-6]>)', r'\\1<bdi dir=\"ltr\">\\2</bdi>\\3', rendered)")
p.write_text(s,encoding='utf8')
