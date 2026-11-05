import pathlib,re,json
base=pathlib.Path(__file__).resolve().parent
out=base/'mermaid_rendered';out.mkdir(exist_ok=True)
text=(base/'02_PROJECT_ARCHITECTURE_AR.md').read_text(encoding='utf8')
blocks=re.findall(r'```mermaid\s*\n(.*?)\n```',text,re.S); assert len(blocks)==10
for i,block in enumerate(blocks,1): (out/f'diagram_{i:02}.mmd').write_text(block+'\n',encoding='utf8')
config={'executablePath':'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe','args':['--no-sandbox','--disable-gpu','--disable-gpu-compositing','--disable-gpu-sandbox','--use-gl=angle','--use-angle=swiftshader','--disable-background-networking']}
(out/'puppeteer.json').write_text(json.dumps(config,indent=2),encoding='utf8')
print('extracted',len(blocks))
