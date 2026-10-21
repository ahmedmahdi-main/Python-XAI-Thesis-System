import argparse
import base64
import html
from pathlib import Path

from xai_finance.storage import read_json
from xai_finance.validation.report import write_report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=Path)
    destination = parser.parse_args().folder.resolve()
    write_report(destination)
    figures = []
    for path in sorted((destination / "figures").glob("*.png")):
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        figures.append(f'<figure><figcaption>{html.escape(path.stem.replace("_", " "))}</figcaption><img alt="{html.escape(path.stem)}" src="data:image/png;base64,{encoded}"></figure>')
    report = html.escape((destination / "SCIENTIFIC_VALIDATION_REPORT.md").read_text(encoding="utf-8"))
    page = '<!doctype html><html lang="en"><meta charset="utf-8"><title>XAI scientific validation</title><style>body{max-width:1200px;margin:40px auto;padding:20px;font:16px system-ui;background:#f7f8fa;color:#17212b}img{max-width:100%}pre{white-space:pre-wrap;font:14px monospace;overflow-wrap:anywhere}figure{background:white;padding:20px;margin:30px 0}figcaption{font-size:22px}</style><h1>Scientific validation: evidence and limitations</h1><p>Offline supplement; original defense package preserved unchanged.</p>' + ''.join(figures) + '<h2>Full report</h2><pre>' + report + '</pre></html>'
    (destination / "offline_validation.html").write_text(page, encoding="utf-8")
    assert read_json(destination / "verification.json")["preservation"]["mismatches"] == []
    print(destination / "SCIENTIFIC_VALIDATION_REPORT.md")
    print(destination / "offline_validation.html")


if __name__ == "__main__":
    main()
