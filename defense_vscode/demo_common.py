"""إعادة تنفيذ الاستدلال المحفوظ؛ لا تدريب ولا اتصال بالشبكة."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUN_ID = "full_20261021T040901084647Z"
RUN = ROOT / "artifacts" / "runs" / RUN_ID
FOLDER = RUN / "AAPL"
OUTPUT = Path(__file__).resolve().parent / "outputs"
# config.py يحدد الجذر من مجلد العمل؛ نثبته هنا حتى يعمل زر VS Code من أي مكان.
os.chdir(ROOT)
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(OUTPUT / ".matplotlib"))
sys.path.insert(0, str(ROOT / "src"))

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from threadpoolctl import threadpool_limits
from xai_finance.data.features import features
from xai_finance.data.windows import build_windows
from xai_finance.evaluate.metrics import forecast_metrics
from xai_finance.io.data_sources import load_snapshot
from xai_finance.models.baselines import persistence
from xai_finance.models.lstm_model import load_lstm
from xai_finance.pipelines.train import load_windows
from xai_finance.storage import read_json, sha256

NAMES = ["LinearRegression", "RandomForest", "GradientBoosting", "LSTM", "Persistence"]


def verified_inputs(name):
    # فحص بصمة ملفات البحث قبل تحميل ملفات النماذج المحلية الموثوقة فقط.
    inventory = read_json(RUN / "inventory.json")
    paths = ["AAPL/windows.npz", "AAPL/data_audit.json", f"AAPL/{name}/predictions.csv"]
    if name in NAMES[:3]:
        paths.append(f"AAPL/{name}.joblib")
    if name == "LSTM":
        paths += ["AAPL/LSTM/best.pt", "AAPL/LSTM/scalers.joblib"]
    for relative in paths:
        if sha256(RUN / relative) != inventory[relative]:
            raise ValueError(f"بصمة الملف لا تطابق السجل: {relative}")
    prices, manifest = load_snapshot("AAPL")  # يتحقق أيضاً من بصمة CSV وعدد صفوفه
    audit = read_json(FOLDER / "data_audit.json")
    if manifest["sha256"] != audit["snapshot"]["sha256"]:
        raise ValueError("لقطة AAPL لا تطابق التجربة المحفوظة")
    saved = load_windows(FOLDER)
    rebuilt = build_windows(features(prices, manifest["frequency"]), audit["lookback"])
    # نتحقق من كل النوافذ والتواريخ والتقسيم؛ الاستدلال يستخدم النوافذ الأصلية المحفوظة.
    np.testing.assert_allclose(rebuilt.x, saved.x, rtol=1e-10, atol=1e-8)
    for field in ("y", "current_close", "trailing_returns"):
        np.testing.assert_allclose(getattr(rebuilt, field), getattr(saved, field), rtol=1e-10, atol=1e-8)
    for field in ("origins", "targets"):
        if not getattr(rebuilt, field).equals(getattr(saved, field)):
            raise ValueError(f"اختلاف التواريخ: {field}")
    if rebuilt.feature_names != saved.feature_names:
        raise ValueError("اختلاف أسماء الخصائص")
    for part in saved.partitions:
        np.testing.assert_array_equal(rebuilt.partitions[part], saved.partitions[part])
    return saved, audit


def run_model(name):
    print(f"\nالنموذج: {name} | الهدف: سعر الإغلاق المعدل للملاحظة التالية")
    print(f"التجربة: {RUN_ID} | AAPL | حساب جديد للاستدلال والتقييم، دون تدريب")
    windows, audit = verified_inputs(name)
    idx = windows.partitions["test"]
    print(f"الخصائص ({len(windows.feature_names)}): {', '.join(windows.feature_names)}")
    print(f"أبعاد النوافذ: {windows.x[idx].shape} = (عدد العينات، طول التسلسل، عدد الخصائص)")
    with threadpool_limits(limits=4):
        if name == "Persistence":
            predicted = persistence(windows.current_close[idx])
            print("خط الأساس يساوي سعر الإغلاق الحالي؛ لا توجد أوزان مدربة.")
        elif name == "LSTM":
            torch.set_num_threads(4)
            checkpoint = torch.load(FOLDER / "LSTM/best.pt", map_location="cpu", weights_only=True)
            model = load_lstm(FOLDER / "LSTM", joblib.load(FOLDER / "LSTM/scalers.joblib"), "cpu")
            print(f"معمارية نقطة الحفظ: {checkpoint['architecture']}; طبقات الشبكة: {model.network}")
            print(f"طول النافذة: {model.lookback}; الخصائص: {model.feature_count}; الجهاز: {model.device}")
            print("تُقيّس المدخلات بمقياس التدريب المحفوظ، ثم يُعكس مقياس الهدف بعد تنبؤ الشبكة.")
            print("حالة hidden تحمل معلومات الإخراج، وcell تحمل ذاكرة LSTM؛ تستخدم الطبقة الخطية آخر hidden.")
            predicted = model.predict(windows.flat[idx])
        else:
            model = joblib.load(FOLDER / f"{name}.joblib")
            if name == "RandomForest":
                model.set_params(n_jobs=1)
            print(f"النموذج المحفوظ ومعلماته: {model}")
            print("يحوّل المشروع النافذة إلى صف؛ التحويلات المدربة داخل النموذج المحفوظ تُطبق تلقائياً.")
            predicted = model.predict(windows.flat[idx])
    original = pd.read_csv(FOLDER / name / "predictions.csv", parse_dates=["feature_cutoff", "target_date"])
    if not pd.DatetimeIndex(original.target_date).equals(windows.targets[idx]) or not pd.DatetimeIndex(original.feature_cutoff).equals(windows.origins[idx]):
        raise ValueError("تواريخ التنبؤات المحفوظة لا تطابق الاختبار")
    np.testing.assert_allclose(original.actual, windows.y[idx], atol=1e-8, rtol=0)
    np.testing.assert_allclose(original.current_close, windows.current_close[idx], atol=1e-8, rtol=0)
    # السماحية مأخوذة من فحص إعادة التحميل الأصلي وتسمح بفروق CPU/GPU الطفيفة.
    np.testing.assert_allclose(predicted, original.predicted, rtol=1e-5, atol=1e-4)
    delta = float(np.max(np.abs(predicted - original.predicted)))
    metrics = forecast_metrics(windows.y[idx], predicted, windows.current_close[idx])
    table = pd.DataFrame({"feature_cutoff": windows.origins[idx], "target_date": windows.targets[idx], "actual": windows.y[idx], "predicted": predicted, "current_close": windows.current_close[idx]})
    out = OUTPUT / name
    out.mkdir(parents=True, exist_ok=True)
    table.to_csv(out / "predictions.csv", index=False)
    import json
    (out / "metrics.json").write_text(json.dumps({"experiment": RUN_ID, "dataset": "AAPL", "provenance": "new CPU inference and evaluation", "max_abs_difference_from_saved_predictions": delta, **metrics}, indent=2, ensure_ascii=False), encoding="utf-8")
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(table.target_date, table.actual, label="Actual", linewidth=1.5)
    ax.plot(table.target_date, table.predicted, label="Predicted", linewidth=1.2)
    ax.set(title=f"AAPL {name}: test set", xlabel="Target date", ylabel="Adjusted close (USD)")
    ax.legend(); ax.grid(alpha=.25); fig.autofmt_xdate(); fig.tight_layout()
    fig.savefig(out / "prediction_vs_actual.png", dpi=140); plt.close(fig)
    print(table.head(10).to_string(index=False))
    print(f"MAE={metrics['mae']:.6f} USD | RMSE={metrics['rmse']:.6f} USD | MAPE={metrics['mape_percent']:.6f}% | R²={metrics['r2']:.6f} | n={metrics['n']}")
    print(f"أقصى فرق عن التنبؤ المحفوظ: {delta:.9g}؛ تمت المقارنة بالسماحية الأصلية.")
    print("كلما انخفض MAE وRMSE كان خطأ السعر أصغر لهذه العينة؛ لا يضمن ذلك الأداء المستقبلي.")
    print(f"النتائج والرسم: {out}")
    return table, metrics


def main(name):
    try:
        run_model(name)
    except Exception as exc:
        print(f"فشل العرض أو التحقق، ولم يُستبدل التنبؤ بنتيجة محفوظة: {exc}", file=sys.stderr)
        raise


def compare():
    rows, reference = [], None
    for name in NAMES:
        table, metrics = run_model(name)
        key = table[["feature_cutoff", "target_date", "actual", "current_close"]]
        if reference is None:
            reference = key
        else:
            pd.testing.assert_frame_equal(reference, key)
        rows.append({"dataset": "AAPL", "experiment": RUN_ID, "model": name, **{k: metrics[k] for k in ["mae", "rmse", "mape_percent", "r2", "n"]}})
    result = pd.DataFrame(rows)
    out = OUTPUT / "comparison"
    out.mkdir(parents=True, exist_ok=True)
    result.to_csv(out / "comparison.csv", index=False)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(result.model, result.rmse, color="steelblue")
    ax.set(title="AAPL common test set: RMSE (lower is better)", ylabel="RMSE (USD)")
    ax.tick_params(axis="x", rotation=18); fig.tight_layout()
    fig.savefig(out / "rmse_comparison.png", dpi=140); plt.close(fig)
    print("\nمقارنة على نفس التواريخ والقيم والهدف:")
    print(result.to_string(index=False))
    print("هذه النتائج تخص تجربة AAPL المحددة؛ لا تثبت تفوقاً عاماً أو أداءً مستقبلياً.")
    print(f"المخرجات: {out}")
