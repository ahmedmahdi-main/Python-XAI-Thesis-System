# شرح `src/xai_finance/cli.py`

بصمة المصدر SHA-256: `1cbd6e8586f7f1830766661cd594ece259adb489650bc9b141e09724f13c2aed`.

تفسير مقابل المصدر، لم تُشغّل الأوامر الموثقة.

## الأسطر 1–6

```python
import argparse
import os

os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")

from xai_finance.config import load_config
```

argparse وos من المكتبة القياسية. setdefault يضبط إعداد CUBLAS إن لم يكن موجوداً قبل استيراد بقية المسار؛ لا يستبدل قيمة موجودة. load_config داخلي لقراءة YAML.

## الأسطر 9–15

```python
def main() -> None:
    parser = argparse.ArgumentParser(description="Reproducible thesis reconstruction")
    parser.add_argument("command", choices=["doctor", "download", "validate", "train", "explain", "evaluate", "report", "all"])
    parser.add_argument("--config", default="configs/default.yaml")
    arguments = parser.parse_args()
    configuration = load_config(arguments.config)
    execute(arguments.command, configuration)
```

main ينشئ محلل سطر الأوامر ويحدد command من الخيارات وconfig الافتراضي، ويقرأ الوسائط والإعداد ثم يستدعي execute؛ الوسيط غير الصالح يوقف argparse برسالة.

## الأسطر 18–20

```python
def execute(command: str, configuration: dict) -> None:
    from xai_finance.io.data_sources import download_all, load_snapshot
    from xai_finance.pipelines.train import resolve_run, train_experiment
```

execute تستقبل الأمر والقاموس وتستورد تحميل البيانات والتدريب وحل مسار التشغيل؛ الاستيراد مؤجل إلى الاستدعاء.

## الأسطر 22–30

```python
    if command == "doctor":
        from xai_finance.environment import verify_environment
        verify_environment()
    if command in {"download", "all"}:
        download_all(configuration)
    if command == "validate":
        for asset in configuration["assets"]:
            prices, manifest = load_snapshot(asset)
            print(asset, len(prices), manifest["sha256"])
```

doctor يستدعي فحص البيئة؛ download وall يستدعيان تنزيل أو تحقق اللقطات؛ validate يحمل كل أصل ويفحصه ويطبع العدد والبصمة. هذه فروع مستقلة وليست سلسلة elif.

## الأسطر 31–38

```python
    if command in {"train", "all"}:
        train_experiment(configuration)
    if command in {"explain", "all"}:
        from xai_finance.pipelines.explain import explain_experiment
        explain_experiment(resolve_run(configuration))
    if command in {"evaluate", "report", "all"}:
        from xai_finance.pipelines.report import generate_report
        generate_report(resolve_run(configuration))
```

train وall يدربان؛ explain وall يفسران آخر تشغيل؛ evaluate وreport وall تستدعي جميعاً generate_report، الذي يقرأ المقاييس ويعيد التحقق ويكتب تقارير. all يسير وفق ترتيب الفروع؛ تشغيل هذه الأوامر قد ينشئ آثاراً ولم ينفذ للتوثيق.

## الأسطر 41–42

```python
if __name__ == "__main__":
    main()
```

حارس __main__ يشغّل main عند التنفيذ كوحدة أو ملف، وليس عند الاستيراد المعتاد.
