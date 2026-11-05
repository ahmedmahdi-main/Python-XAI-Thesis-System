import pathlib,re,urllib.parse
root=pathlib.Path(__file__).resolve().parent
missing=[]; checked=0
excluded={'mermaid_tool','.npm-cache','node_modules','edge_preview_profile','edge_cpu_preview','edge_cpu_print','edge_figure_print','edge_figure_print_v2','edge_figure_print_v3','edge_figure_print_v4'}
for page in root.rglob('*.md'):
 if any(part in excluded or part.startswith('edge_') for part in page.relative_to(root).parts): continue
 checked+=1
 text=page.read_text(encoding='utf-8-sig')
 for target in re.findall(r'\]\(([^)]+)\)',text):
  if target.startswith(('http:', 'https:', '#', 'mailto:')): continue
  target=urllib.parse.unquote(target.split('#',1)[0]).strip('<>')
  if target and not (page.parent/target).exists(): missing.append((str(page.relative_to(root)),target))
print('checked first-party Markdown pages:',checked,'unresolved local file links:',len(missing))
for page,target in missing: print(page,'->',target)
if missing: raise SystemExit(1)
