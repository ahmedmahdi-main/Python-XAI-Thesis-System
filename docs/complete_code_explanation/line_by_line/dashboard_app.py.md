# شرح `dashboard/app.py`

بصمة المصدر SHA-256: `e0bc35adc2b56a65578fbd8c18c38f4168f8c6df24a48e8c68001637575286a7`.

واجهة Streamlit لقراءة الآثار المحفوظة. تنشئ دوال العرض عناصر واجهة وتقرأ CSV وJSON وNPZ وصوراً وتقارير محلية؛ لا تُدرّب نموذجاً أو تُجري استدلالاً حياً. يربط main الدوال الثماني بتبويباتها. أخطاء الملفات المطلوبة غير ملتقطة عموماً، باستثناء فحوص الوجود الموضحة أدناه.

كل مقطع مقتبس آلياً من الملف المحدد؛ الأسطر الفارغة للفصل والتنسيق. التفسير من مراجعة المصدر ولا يمثل اختبار تشغيل للواجهة.

## السطر 1

```python
"""Saved-artifact research dashboard; viewing never downloads data or refits models."""
```

توثق السلسلة أن الواجهة تعرض الآثار المحفوظة ولا تجري تنزيل البيانات أو إعادة ملاءمة النماذج عند المشاهدة.

## الأسطر 3–4

```python
from pathlib import Path
import json
```

Path وjson من المكتبة القياسية: الأول للمسارات والثاني لفك JSON.

## الأسطر 6–10

```python
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
```

مكتبات خارجية: NumPy للمصفوفات وملف NPZ؛ pandas لجداول CSV؛ plotly.express وgraph_objects للرسوم؛ Streamlit لبناء الواجهة وتخزين البيانات مؤقتاً.

## الأسطر 12–13

```python
ROOT = Path(__file__).resolve().parents[1]
st.set_page_config(page_title="Saleh | Financial XAI research", page_icon="◈", layout="wide")
```

يحسب ROOT من أصل مجلد dashboard ويهيئ عنوان الصفحة والرمز والتخطيط العريض؛ لهذا استدعاء واجهة عند تحميل الملف.

## الأسطر 14–19

```python
st.markdown("""<style>
 .block-container {max-width:1480px;padding-top:2rem}
 h1 {font-family:Georgia,serif;font-weight:500;letter-spacing:-.035em}
 [data-testid='stMetric'] {border-top:3px solid #22577a;padding-top:.7rem}
 .research-strip {border-left:5px solid #b15b24;padding:.8rem 1rem;background:#e9eff5;margin-bottom:1rem}
 </style>""", unsafe_allow_html=True)
```

يمرر CSS ثابتاً إلى st.markdown مع السماح بـ HTML لضبط العرض والخط والبطاقات والشريط؛ ليست هذه الحسابات نموذجاً أو بيانات بحثية.

## الأسطر 22–23

```python
def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))
```

read_json يستقبل Path، يقرأ النص UTF-8 ويفك JSON ويعيد كائناً بحسب محتواه. أخطاء غياب الملف أو فساد JSON غير ملتقطة هنا. يستعمله معظم دوال العرض.

## الأسطر 26–28

```python
@st.cache_data
def load_table(path: str, modification_time: float) -> pd.DataFrame:
    return pd.read_csv(path)
```

يخزن decorator ‏st.cache_data ناتج load_table؛ تقرأ الدالة CSV وتعيد DataFrame. مع أن modification_time لا يستخدم داخل الجسم فهو جزء من مدخلات التخزين المؤقت لتغيير المفتاح عند تغير وقت الملف.

## الأسطر 31–32

```python
def csv_table(path: Path) -> pd.DataFrame:
    return load_table(str(path), path.stat().st_mtime)
```

csv_table تستقبل Path وتمرير اسمه ووقت تعديله إلى load_table؛ stat قد يرفع استثناء إذا لم يوجد الملف. يستخدمها العرض والتقييم المحفوظ.

## الأسطر 35–39

```python
def saved_image(path: Path, caption: str) -> None:
    if path.exists():
        st.image(str(path), caption=caption, use_container_width=True)
    else:
        st.info("This artifact has not been generated. Run the explain/report command shown in Reproducibility.")
```

saved_image تعرض صورة محلية مع تعليق إذا وُجدت وإلا تعرض رسالة معلومات. المدخل مسار وتعليق؛ أثرها عرض Streamlit وليس إنشاء صورة، ولا تعالج ملف صورة فاسداً.

## الأسطر 42–47

```python
def overview(metadata: dict, audit: dict) -> None:
    st.subheader("A forecast with an evidence trail")
    st.write("Predict the next observed close from information through the preceding close. Compare four models with persistence, then inspect SHAP and LIME explanations of the same saved predictions.")
    st.markdown("**Observed history → trailing features → chronological 80/10/10 → fitted models → untouched test → explanations**")
    st.write("Researcher: Mohammad Saleh · Damghan University · Reconstruction for defense")
    st.caption("New computations and historical thesis claims are stored separately. Explanations describe model associations; they do not establish causality, trading profitability or improved human trust.")
```

overview تقبل بيانات التشغيل والتدقيق وتعرض الغرض والتسلسل والباحث والتحذير من استنتاج السببية أو الربح أو الثقة البشرية؛ هي عرض نصي وليس حساباً.

## الأسطر 48–51

```python
    flow = ROOT / "artifacts/runs" / metadata["run_id"] / "plots/research_flow.png"
    if flow.exists():
        saved_image(flow, "Implemented chronological forecasting and explanation protocol.")
    st.json({"run_id": metadata["run_id"], "status": metadata["status"], "target": audit["target"], "units": audit["snapshot"]["units"]}, expanded=True)
```

يبني مسار صورة تدفق البحث باستخدام run_id ويعرضها إن وجدت، ثم يعرض معرّف التشغيل وحالته والهدف والوحدات من القواميس. مفاتيح ناقصة قد ترفع KeyError.

## الأسطر 54–61

```python
def preprocessing(folder: Path, audit: dict) -> None:
    st.subheader("What the model could know")
    snapshot = ROOT / "data/raw" / f"{folder.name}.csv"
    if snapshot.exists():
        history = csv_table(snapshot)
        price = "adj_close" if audit["snapshot"]["frequency"] == "daily" else "close"
        st.plotly_chart(px.line(history, x="date", y=price, title="Historical dataset snapshot"), use_container_width=True)
        st.caption("Saved provider snapshot in original units; no live data request.")
```

preprocessing تقبل مجلد الأصل وبيانات تدقيقه. تبني مسار CSV محلي باسم المجلد، وإذا وُجد تقرأه وتختار adj_close لليومي وclose لغيره ثم ترسم التاريخ؛ لا تقدم طلباً حياً.

## الأسطر 62–67

```python
    st.dataframe(pd.DataFrame(audit["split"]).T, use_container_width=True)
    saved_image(folder / "plots/temporal_split.png", "Target dates remain chronological; validation and test transformations are frozen.")
    st.write("Every model receives the same complete historical window. Tabular models flatten it; LSTM preserves its time axis.")
    st.write("Features:", ", ".join(audit["features"]))
    st.json(audit["snapshot"], expanded=False)
    st.caption(f"Lookback {audit['lookback']}; feature warm-up rows removed: {audit['feature_rows_dropped_warmup']}. Missing records are dropped without interpolation or target filling.")
```

تعرض تقسيم التواريخ بصورة جدول، وصورة التقسيم إن وُجدت، ووصف شكل مدخلات النماذج وأسماء السمات ومصدر اللقطة وطول النافذة وعدد الصفوف المحذوفة. هذه عبارات واجهة؛ تدقيق صحتها يستلزم شيفرة التحضير.

## الأسطر 70–73

```python
def forecasting(predictions: pd.DataFrame, folder: Path) -> None:
    st.info("Saved prediction replay: these forecasts were produced by the recorded experiment. Viewing this chart does not run live inference.")
    model = st.selectbox("Forecast model", sorted(predictions.model.unique()), key="forecast_model")
    selected = predictions[predictions.model == model]
```

forecasting تستقبل DataFrame التنبؤات ومجلد الأصل. تحذر من إعادة العرض وتتيح اختيار نموذج من القيم الموجودة ثم ترشح الصفوف؛ لا تستدعي predict.

## الأسطر 74–79

```python
    figure = go.Figure()
    figure.add_scatter(x=selected.target_date, y=selected.actual, name="Actual", line={"color": "#22374a"})
    figure.add_scatter(x=selected.target_date, y=selected.predicted, name=model, line={"color": "#b15b24"})
    figure.update_layout(height=420, xaxis_title="Held-out target date", yaxis_title="Original target units")
    st.plotly_chart(figure, use_container_width=True)
    st.dataframe(selected[["feature_cutoff", "target_date", "actual", "predicted", "current_close"]], use_container_width=True)
```

تنشئ Figure وخطي القيم الفعلية والمتوقعة وفق target_date وتضبط المحاور ثم تعرض الرسم وجدول تواريخ المدخل والهدف والقيم؛ الوحدات أصلية بحسب الأثر المحفوظ.

## الأسطر 80–82

```python
    with st.expander("Next observation after the saved snapshot"):
        st.warning("Unverified extrapolation after the snapshot cutoff. This is not a current live-market forecast.")
        st.json(read_json(folder / "next_forecast.json"))
```

داخل expander تعرض تحذيراً ثم تقرأ next_forecast.json: توقع محفوظ غير متحقق يتجاوز نهاية اللقطة، وليس توقعاً للسوق الحالي. لا يوجد فحص وجود للملف هنا.

## الأسطر 85–88

```python
def comparison(folder: Path) -> None:
    metrics = pd.DataFrame(read_json(folder / "metrics.json"))
    training = read_json(folder / "training.json")
    metrics["training_seconds"] = metrics.model.map({name: audit["training_seconds"] for name, audit in training.items()}).fillna(0)
```

comparison تقرأ metrics.json وtraining.json؛ تربط اسم النموذج بزمن تدريبه وتمثل القيمة غير الموجودة بصفر. هذا الصفر بديل للعرض ولا يثبت زمن تدريب مقاساً للمرجع.

## الأسطر 89–92

```python
    st.dataframe(metrics[["model", "mae", "rmse", "mape_percent", "r2", "direction_accuracy", "n", "training_seconds"]], use_container_width=True, hide_index=True)
    metric = st.selectbox("Comparison measure", ["mae", "rmse", "r2", "direction_accuracy"], key="comparison_metric")
    st.plotly_chart(px.bar(metrics, x="model", y=metric, color="model"), use_container_width=True)
    st.caption("Price-level R2 can be high for persistence. Model rankings here describe this dataset and split; they do not establish investment value.")
```

تعرض المقاييس وعدد العينات والزمن وتتيح اختيار مقياس لرسم أعمدة؛ تنبه إلى أن R² المرتفع لا يثبت قيمة استثمارية وأن الترتيب مرتبط بالبيانات والتقسيم.

## الأسطر 95–100

```python
def explanations(folder: Path) -> None:
    model = st.selectbox("Explain model", ["LinearRegression", "RandomForest", "GradientBoosting", "LSTM"], key="explain_model")
    explanation_folder = folder / model / "explanations"
    if not (explanation_folder / "quality.json").exists():
        st.info("No saved explanations yet. Run python -m xai_finance.cli explain --config configs/full_experiment.yaml")
        return
```

explanations تتيح اختيار أحد النماذج الأربعة وتحدد مجلد تفسيره. إذا غاب quality.json تعرض إرشاداً وتعود مبكراً، فلا تحاول قراءة بقية الآثار.

## الأسطر 101–108

```python
    quality = read_json(explanation_folder / "quality.json")
    date = st.selectbox("Held-out target date (precomputed subset)", quality["target_dates"], key="explanation_date")
    position = quality["target_dates"].index(date)
    with np.load(explanation_folder / "shap.npz", allow_pickle=False) as saved:
        signed = saved["values"][position]
        names = saved["feature_names"].astype(str)
        baseline = float(np.asarray(saved["base_values"]).ravel()[position])
        index = int(saved["indices"][position])
```

تقرأ جودة التفسير وتختار تاريخ هدف من المجموعة المحسوبة مسبقاً وتجد موضعه. تفتح shap.npz مع allow_pickle=False ثم تستخرج الإسهامات وأسماء السمات والقيمة الأساسية وفهرس العينة؛ تفترض توافق ترتيب المصفوفات مع التواريخ.

## الأسطر 109–112

```python
    order = np.argsort(np.abs(signed))[-12:]
    st.caption(f"Feature cutoff: {quality['feature_cutoffs'][position]} · SHAP baseline: {baseline:.5g} · forecast: {baseline + signed.sum():.5g} (original units)")
    local = pd.DataFrame({"feature": names[order], "SHAP contribution": signed[order]})
    st.plotly_chart(px.bar(local, x="SHAP contribution", y="feature", orientation="h", color="SHAP contribution", color_continuous_scale="RdBu"), use_container_width=True)
```

ترتب الإسهامات بالقيمة المطلقة وتختار آخر 12 فهرساً، وتعرض تاريخ نهاية المعلومات والقيمة الأساسية ومجموعها مع جميع الإسهامات، ثم ترسم السمات الاثنتي عشرة. المعروض في الرسم مختزل لكن الجمع يستخدم signed كاملاً.

## الأسطر 113–116

```python
    lime = read_json(explanation_folder / f"lime_{index}.json")
    st.write("LIME local surrogate for the same observation")
    st.dataframe(pd.DataFrame(lime["features"], columns=["Feature condition", "Local weight"]), hide_index=True, use_container_width=True)
    st.caption(f"Model {lime['model_prediction']:.5g}; local approximation {lime['local_surrogate_prediction']:.5g}; absolute error {lime['absolute_local_error']:.5g}; neighborhood R2 {lime['weighted_neighborhood_r2']:.4g}.")
```

تقرأ lime_<index>.json للعينة نفسها، وتعرض شروط السمات وأوزان النموذج البديل وتنبؤ النموذج والبديل والخطأ المطلق وR² الجوار المحفوظ. هي لا تولد اضطرابات جديدة.

## الأسطر 117–124

```python
    first, second = st.columns(2)
    with first:
        saved_image(explanation_folder / "global_importance.png", "Mean sum of absolute lag contributions on the declared subset.")
    with second:
        saved_image(explanation_folder / "feature_time_heatmap.png", "First declared observation only; signed contributions by feature and window position.")
    with st.expander("Fidelity, seed stability, overhead and limitations"):
        st.json(quality)
    st.warning("Correlated-feature masking and local sampling may create implausible combinations. These are model explanations, not causes or investment advice.")
```

تنشئ عمودين لصور الأهمية العالمية وخريطة الزمن المحفوظتين وتعرض quality في expander ثم تحذر من التركيبات غير الواقعية والخلط بين التفسير والسببية. saved_image تعالج غياب الصورتين فقط.

## الأسطر 127–131

```python
def regimes(folder: Path) -> None:
    st.write("A priori regime: trailing 20 observations return >+5% bull, <-5% bear, otherwise sideways. Monthly means 20 months. Only information through the feature cutoff is used.")
    table = pd.DataFrame(read_json(folder / "regimes.json"))
    st.dataframe(table[["model", "regime", "n", "mae", "rmse", "direction_accuracy"]], hide_index=True, use_container_width=True)
    saved_image(folder / "plots/regime_errors.png", "Small regime groups are descriptive; no unobserved regimes or winners are invented.")
```

regimes تعرض تعريف الحالات النصي ثم تقرأ regimes.json وتعرض عدد وأخطاء كل مجموعة وصورة محفوظة. النص يصف عتبة 5% ثابتة في الواجهة؛ يجب مقارنة إعداد التشغيل الفعلي قبل تعميمه.

## الأسطر 132–134

```python
    path = folder / "LSTM/explanations/regime_drivers.csv"
    if path.exists():
        st.dataframe(csv_table(path), use_container_width=True)
```

إذا وُجد regime_drivers.csv تحت تفسير LSTM، تقرأه وتعرضه؛ عدم وجوده لا يوقف الواجهة.

## الأسطر 137–140

```python
def reproducibility(metadata: dict, folder: Path) -> None:
    st.write("This dashboard reads local artifacts and never trains, downloads or recalculates model selection.")
    st.code("python -m xai_finance.cli doctor\npython -m xai_finance.cli validate --config configs/full_experiment.yaml\npython -m pytest -q\npython -m xai_finance.cli explain --config configs/full_experiment.yaml\npython -m xai_finance.cli report --config configs/full_experiment.yaml")
    st.json(metadata, expanded=False)
```

reproducibility تعرض وصف إعادة التشغيل وأوامراً كنص عبر st.code وتعرض metadata؛ عرض النص لا ينفذ الأوامر أو يعيد التدريب.

## الأسطر 141–147

```python
    if (folder / "RESULTS.md").exists():
        st.download_button("Download computed research report", (folder / "RESULTS.md").read_bytes(), "RESULTS.md")
    if (folder / "inventory.json").exists():
        st.download_button("Download artifact hash inventory", (folder / "inventory.json").read_bytes(), "inventory.json")
    tests = ROOT / "artifacts/tests/summary.json"
    if tests.exists():
        st.json(read_json(tests))
```

تضيف أزرار تنزيل للتقرير وفهرس الهاش إذا وجدا وتعرض ملخص الاختبارات إن وُجد. read_bytes يقرأ الملفات ولا يكتبها؛ التنزيل استجابة لتفاعل المستخدم.

## الأسطر 148–155

```python
    validations = sorted((ROOT / "artifacts/scientific_validation").glob("*/protocol.json"))
    if validations:
        with st.expander("Saved scientific validation results"):
            selected = st.selectbox("Scientific validation", validations, format_func=lambda path: path.parent.name, key="scientific_validation")
            validation = selected.parent
            protocol = read_json(selected)
            st.write(protocol["status"])
            st.caption(f"Original experiment: {protocol['original_run']}. Results below retain the recorded model rankings and limitations.")
```

تبحث عن protocol.json في مجلدات التحقق العلمي وترتبها؛ إن وجدت تنشئ expander واختياراً بصيغة اسم المجلد ثم تقرأ البروتوكول وتعرض حالته ومعرّف التجربة الأصلية.

## الأسطر 156–159

```python
            st.dataframe(csv_table(validation / "new_metrics.csv"), use_container_width=True, hide_index=True)
            st.download_button("Download scientific validation report", (validation / "SCIENTIFIC_VALIDATION_REPORT.md").read_bytes(), "SCIENTIFIC_VALIDATION_REPORT.md")
            st.download_button("Download standalone offline validation page", (validation / "offline_validation.html").read_bytes(), "offline_validation.html", mime="text/html")
    st.caption("Trusted locally generated joblib/checkpoint files only. Viewing this dashboard does not deserialize model files.")
```

تعرض new_metrics.csv وأزرار تنزيل تقرير وصفحة تحقق محفوظين، ثم توضح أن الواجهة لا تفك تسلسل ملفات النماذج. الملفات الثلاثة داخل هذا الفرع مطلوبة دون فحص وجود منفصل.

## الأسطر 162–168

```python
def thesis_alignment(folder: Path) -> None:
    historical = read_json(ROOT / "docs/thesis_reported_reference.json")
    first, second = st.columns(2)
    with first:
        st.write("THESIS_REPORTED_NOT_REPRODUCED")
        st.dataframe(pd.DataFrame(historical["models"]), hide_index=True)
        st.caption("Table 4, Chapter 4 section 4.2, P1026-P1049; TOC p101. Historical dataset and units unspecified.")
```

thesis_alignment تقرأ المرجع التاريخي، تنشئ عمودين، وتعرض في الأول نماذج الرسالة مع تنبيه عدم إعادة الإنتاج ونقص الوحدات والبيانات.

## الأسطر 169–176

```python
    with second:
        st.write("NEWLY_COMPUTED")
        st.dataframe(pd.DataFrame(read_json(folder / "metrics.json"))[["model", "mae", "rmse", "r2"]], hide_index=True)
    st.warning("The tables have different/unspecified historical units and datasets; numerical differences are not replication errors or evidence of improvement.")
    st.write("Historical survey percentages 78%, 85%, 70% are verified in the thesis text, but participant counts and raw responses are unavailable. No new survey was conducted.")
    st.write("The appendix screenshots train Decision Tree/XGBoost on missing ether.csv, use an 80/20 split and full-data mean imputation, and show no next-day target shift. This reconstruction follows the narrative's four models and corrects temporal leakage risks.")
    with st.expander("Verified source traceability"):
        st.markdown((ROOT / "docs/THESIS_TRACEABILITY.md").read_text(encoding="utf-8"))
```

في العمود الثاني تعرض مقاييس التجربة الحالية، وتحذر من المقارنة العددية غير المتجانسة، وتعرض وصف الاستبيان والملحق وتتبع المصدر من ملف Markdown. هذه ادعاءات من نص الواجهة تحتاج مطابقتها بالمصدر العلمي مستقلاً.

## الأسطر 179–183

```python
def main() -> None:
    st.title("Financial forecasts, explained")
    st.caption("MOHAMMAD SALEH · MASTER'S THESIS RECONSTRUCTION · SAVED RESEARCH EVIDENCE")
    runs = sorted((ROOT / "artifacts/runs").glob("*/run.json"), reverse=True)
    available = [path.parent for path in runs if read_json(path).get("assets_completed") and read_json(path)["status"] != "SUPERSEDED_DIAGNOSTIC_NOT_FINAL"]
```

main نقطة تجميع الواجهة؛ تعرض العنوان ثم تجمع run.json تحت artifacts/runs وتحتفظ بالتشغيلات ذات assets_completed غير الموسومة superseded. قد ترفع قراءة JSON استثناء عند ملف تالف؛ تعاد قراءته مرتين لبعض المرشحين.

## الأسطر 184–187

```python
    preferred = ROOT / "artifacts/latest_full.json"
    if preferred.exists():
        run_id = read_json(preferred)["run_id"]
        available.sort(key=lambda path: (path.name == run_id, path.name), reverse=True)
```

إذا وجد latest_full.json يستخرج run_id ويرتب التشغيل المفضل أولاً ثم الاسم تنازلياً. وجود المؤشر لا يضمن أن التشغيل المشار إليه من ضمن المتاح.

## الأسطر 188–191

```python
    if not available:
        st.info("No saved experiment is ready. Prepare it with the commands below.")
        st.code("python -m xai_finance.cli download --config configs/quick_demo.yaml\npython -m xai_finance.cli train --config configs/quick_demo.yaml\npython -m xai_finance.cli explain --config configs/quick_demo.yaml\npython -m xai_finance.cli report --config configs/quick_demo.yaml")
        return
```

إذا لم توجد تشغيلات متاحة يعرض رسالة وأوامراً نصية لإعداد تجربة ثم يرجع مبكراً؛ الأوامر لا تنفذ تلقائياً.

## الأسطر 192–197

```python
    run_folder = st.sidebar.selectbox("Saved experiment", available, format_func=lambda path: path.name, key="run")
    metadata = read_json(run_folder / "run.json")
    asset = st.sidebar.selectbox("Dataset", metadata["assets_completed"], key="asset")
    folder = run_folder / asset
    audit = read_json(folder / "data_audit.json")
    st.markdown(f"<div class='research-strip'><b>{asset}</b> · {audit['snapshot']['units']} · TEST {audit['split']['test']['target_start']} — {audit['split']['test']['target_end']}</div>", unsafe_allow_html=True)
```

يختار المستخدم التشغيل والأصل من الشريط الجانبي؛ تقرأ metadata وdata_audit وتحدد المجلد وتعرض الأصل ووحدة القياس وحدود أهداف الاختبار. يستخدم HTML في شريط نصي مركب من بيانات محفوظة.

## الأسطر 198–200

```python
    if audit["snapshot"]["frequency"] == "monthly":
        st.warning("Separate monthly retrospective index experiment. Revised data and unknown release vintages prevent a publication-time forecasting claim.")
    predictions = csv_table(folder / "predictions.csv")
```

إذا كان التردد شهرياً يعرض تحذير البيانات المنقحة وأزمنة النشر؛ يقرأ predictions.csv المحفوظ في جميع الأحوال قبل بناء التبويبات.

## الأسطر 201–205

```python
    tabs = st.tabs(["Overview", "Data & preprocessing", "Forecasting", "Compare models", "Explain predictions", "Regimes", "Reproducibility", "Thesis alignment"])
    renderers = [lambda: overview(metadata, audit), lambda: preprocessing(folder, audit), lambda: forecasting(predictions, folder), lambda: comparison(folder), lambda: explanations(folder), lambda: regimes(folder), lambda: reproducibility(metadata, run_folder), lambda: thesis_alignment(folder)]
    for tab, render in zip(tabs, renderers):
        with tab:
            render()
```

ينشئ ثمانية تبويبات وقائمة دوال lambda تؤخر نداء كل عارض إلى الحلقة، ثم يربط كل تبويب بعارضه عبر zip ويدخله بـ with وينفذه. لا تتضمن الشيفرة شرطاً يمنع تنفيذ عارض التبويب غير المحدد؛ تتطلب ملفات جميع العارضات ذاتها عند إعادة تشغيل الصفحة.

## الأسطر 208–209

```python
if __name__ == "__main__":
    main()
```

عند التنفيذ باسم __main__ يستدعي main. يستعمل main.py قيمة run_name هذه، وكذلك تشغيل app.py مباشرة؛ الاستيراد باسم آخر لا يستدعي main وإن كانت تهيئة المستوى الأعلى تنفذ.
