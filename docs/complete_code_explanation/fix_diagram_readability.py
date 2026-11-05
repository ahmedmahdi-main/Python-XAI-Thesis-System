from pathlib import Path
p=Path('docs/complete_code_explanation/02_PROJECT_ARCHITECTURE_AR.md')
s=p.read_text(encoding='utf-8-sig')
s=s.replace('## 1. البنية العامة\n\n```mermaid\nflowchart LR','## 1. البنية العامة\n\n```mermaid\nflowchart TD')
s=s.replace('## 5. LSTM المنفذ\n\n```mermaid\nflowchart LR','## 5. LSTM المنفذ\n\n```mermaid\nflowchart TD')
s=s.replace('LI --> Q2[خطأ البديل المحلي و R2 الجوار]','LI --> Q2["خطأ البديل المحلي<br/>R² الجوار"]')
p.write_text(s,encoding='utf8')
