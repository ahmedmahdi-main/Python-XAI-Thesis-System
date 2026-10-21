"""Saved-artifact research dashboard; viewing never downloads data or refits models."""

from pathlib import Path
import json

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
st.set_page_config(page_title="Saleh | Financial XAI research", page_icon="◈", layout="wide")
st.markdown("""<style>
 .block-container {max-width:1480px;padding-top:2rem}
 h1 {font-family:Georgia,serif;font-weight:500;letter-spacing:-.035em}
 [data-testid='stMetric'] {border-top:3px solid #22577a;padding-top:.7rem}
 .research-strip {border-left:5px solid #b15b24;padding:.8rem 1rem;background:#e9eff5;margin-bottom:1rem}
 </style>""", unsafe_allow_html=True)


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


@st.cache_data
def load_table(path: str, modification_time: float) -> pd.DataFrame:
    return pd.read_csv(path)


def csv_table(path: Path) -> pd.DataFrame:
    return load_table(str(path), path.stat().st_mtime)


def saved_image(path: Path, caption: str) -> None:
    if path.exists():
        st.image(str(path), caption=caption, use_container_width=True)
    else:
        st.info("This artifact has not been generated. Run the explain/report command shown in Reproducibility.")


def overview(metadata: dict, audit: dict) -> None:
    st.subheader("A forecast with an evidence trail")
    st.write("Predict the next observed close from information through the preceding close. Compare four models with persistence, then inspect SHAP and LIME explanations of the same saved predictions.")
    st.markdown("**Observed history → trailing features → chronological 80/10/10 → fitted models → untouched test → explanations**")
    st.write("Researcher: Mohammad Saleh · Damghan University · Reconstruction for defense")
    st.caption("New computations and historical thesis claims are stored separately. Explanations describe model associations; they do not establish causality, trading profitability or improved human trust.")
    flow = ROOT / "artifacts/runs" / metadata["run_id"] / "plots/research_flow.png"
    if flow.exists():
        saved_image(flow, "Implemented chronological forecasting and explanation protocol.")
    st.json({"run_id": metadata["run_id"], "status": metadata["status"], "target": audit["target"], "units": audit["snapshot"]["units"]}, expanded=True)


def preprocessing(folder: Path, audit: dict) -> None:
    st.subheader("What the model could know")
    st.dataframe(pd.DataFrame(audit["split"]).T, use_container_width=True)
    saved_image(folder / "plots/temporal_split.png", "Target dates remain chronological; validation and test transformations are frozen.")
    st.write("Every model receives the same complete historical window. Tabular models flatten it; LSTM preserves its time axis.")
    st.write("Features:", ", ".join(audit["features"]))
    st.json(audit["snapshot"], expanded=False)
    st.caption(f"Lookback {audit['lookback']}; feature warm-up rows removed: {audit['feature_rows_dropped_warmup']}. Missing records are dropped without interpolation or target filling.")


def forecasting(predictions: pd.DataFrame, folder: Path) -> None:
    model = st.selectbox("Forecast model", sorted(predictions.model.unique()), key="forecast_model")
    selected = predictions[predictions.model == model]
    figure = go.Figure()
    figure.add_scatter(x=selected.target_date, y=selected.actual, name="Actual", line={"color": "#22374a"})
    figure.add_scatter(x=selected.target_date, y=selected.predicted, name=model, line={"color": "#b15b24"})
    figure.update_layout(height=420, xaxis_title="Held-out target date", yaxis_title="Original target units")
    st.plotly_chart(figure, use_container_width=True)
    st.dataframe(selected[["feature_cutoff", "target_date", "actual", "predicted", "current_close"]], use_container_width=True)
    with st.expander("Next observation after the saved snapshot"):
        st.warning("Unverified extrapolation after the snapshot cutoff. This is not a current live-market forecast.")
        st.json(read_json(folder / "next_forecast.json"))


def comparison(folder: Path) -> None:
    metrics = pd.DataFrame(read_json(folder / "metrics.json"))
    training = read_json(folder / "training.json")
    metrics["training_seconds"] = metrics.model.map({name: audit["training_seconds"] for name, audit in training.items()}).fillna(0)
    st.dataframe(metrics[["model", "mae", "rmse", "mape_percent", "r2", "direction_accuracy", "n", "training_seconds"]], use_container_width=True, hide_index=True)
    metric = st.selectbox("Comparison measure", ["mae", "rmse", "r2", "direction_accuracy"], key="comparison_metric")
    st.plotly_chart(px.bar(metrics, x="model", y=metric, color="model"), use_container_width=True)
    st.caption("Price-level R2 can be high for persistence. Model rankings here describe this dataset and split; they do not establish investment value.")


def explanations(folder: Path) -> None:
    model = st.selectbox("Explain model", ["LinearRegression", "RandomForest", "GradientBoosting", "LSTM"], key="explain_model")
    explanation_folder = folder / model / "explanations"
    if not (explanation_folder / "quality.json").exists():
        st.info("No saved explanations yet. Run python -m xai_finance.cli explain --config configs/full_experiment.yaml")
        return
    quality = read_json(explanation_folder / "quality.json")
    date = st.selectbox("Held-out target date (precomputed subset)", quality["target_dates"], key="explanation_date")
    position = quality["target_dates"].index(date)
    with np.load(explanation_folder / "shap.npz", allow_pickle=False) as saved:
        signed = saved["values"][position]
        names = saved["feature_names"].astype(str)
        baseline = float(np.asarray(saved["base_values"]).ravel()[position])
        index = int(saved["indices"][position])
    order = np.argsort(np.abs(signed))[-12:]
    st.caption(f"Feature cutoff: {quality['feature_cutoffs'][position]} · SHAP baseline: {baseline:.5g} · forecast: {baseline + signed.sum():.5g} (original units)")
    local = pd.DataFrame({"feature": names[order], "SHAP contribution": signed[order]})
    st.plotly_chart(px.bar(local, x="SHAP contribution", y="feature", orientation="h", color="SHAP contribution", color_continuous_scale="RdBu"), use_container_width=True)
    lime = read_json(explanation_folder / f"lime_{index}.json")
    st.write("LIME local surrogate for the same observation")
    st.dataframe(pd.DataFrame(lime["features"], columns=["Feature condition", "Local weight"]), hide_index=True, use_container_width=True)
    st.caption(f"Model {lime['model_prediction']:.5g}; local approximation {lime['local_surrogate_prediction']:.5g}; absolute error {lime['absolute_local_error']:.5g}; neighborhood R2 {lime['weighted_neighborhood_r2']:.4g}.")
    first, second = st.columns(2)
    with first:
        saved_image(explanation_folder / "global_importance.png", "Mean sum of absolute lag contributions on the declared subset.")
    with second:
        saved_image(explanation_folder / "feature_time_heatmap.png", "First declared observation only; signed contributions by feature and window position.")
    with st.expander("Fidelity, seed stability, overhead and limitations"):
        st.json(quality)
    st.warning("Correlated-feature masking and local sampling may create implausible combinations. These are model explanations, not causes or investment advice.")


def regimes(folder: Path) -> None:
    st.write("A priori regime: trailing 20 observations return >+5% bull, <-5% bear, otherwise sideways. Monthly means 20 months. Only information through the feature cutoff is used.")
    table = pd.DataFrame(read_json(folder / "regimes.json"))
    st.dataframe(table[["model", "regime", "n", "mae", "rmse", "direction_accuracy"]], hide_index=True, use_container_width=True)
    saved_image(folder / "plots/regime_errors.png", "Small regime groups are descriptive; no unobserved regimes or winners are invented.")
    path = folder / "LSTM/explanations/regime_drivers.csv"
    if path.exists():
        st.dataframe(csv_table(path), use_container_width=True)


def reproducibility(metadata: dict, folder: Path) -> None:
    st.write("This dashboard reads local artifacts and never trains, downloads or recalculates model selection.")
    st.code("python -m xai_finance.cli doctor\npython -m xai_finance.cli validate --config configs/full_experiment.yaml\npython -m pytest -q\npython -m xai_finance.cli explain --config configs/full_experiment.yaml\npython -m xai_finance.cli report --config configs/full_experiment.yaml")
    st.json(metadata, expanded=False)
    if (folder / "RESULTS.md").exists():
        st.download_button("Download computed research report", (folder / "RESULTS.md").read_bytes(), "RESULTS.md")
    if (folder / "inventory.json").exists():
        st.download_button("Download artifact hash inventory", (folder / "inventory.json").read_bytes(), "inventory.json")
    tests = ROOT / "artifacts/tests/summary.json"
    if tests.exists():
        st.json(read_json(tests))
    st.caption("Trusted locally generated joblib/checkpoint files only. Viewing this dashboard does not deserialize model files.")


def thesis_alignment(folder: Path) -> None:
    historical = read_json(ROOT / "docs/thesis_reported_reference.json")
    first, second = st.columns(2)
    with first:
        st.write("THESIS_REPORTED_NOT_REPRODUCED")
        st.dataframe(pd.DataFrame(historical["models"]), hide_index=True)
        st.caption("Table 4, Chapter 4 section 4.2, P1026-P1049; TOC p101. Historical dataset and units unspecified.")
    with second:
        st.write("NEWLY_COMPUTED")
        st.dataframe(pd.DataFrame(read_json(folder / "metrics.json"))[["model", "mae", "rmse", "r2"]], hide_index=True)
    st.warning("The tables have different/unspecified historical units and datasets; numerical differences are not replication errors or evidence of improvement.")
    st.write("Historical survey percentages 78%, 85%, 70% are verified in the thesis text, but participant counts and raw responses are unavailable. No new survey was conducted.")
    st.write("The appendix screenshots train Decision Tree/XGBoost on missing ether.csv, use an 80/20 split and full-data mean imputation, and show no next-day target shift. This reconstruction follows the narrative's four models and corrects temporal leakage risks.")
    with st.expander("Verified source traceability"):
        st.markdown((ROOT / "docs/THESIS_TRACEABILITY.md").read_text(encoding="utf-8"))


def main() -> None:
    st.title("Financial forecasts, explained")
    st.caption("MOHAMMAD SALEH · MASTER'S THESIS RECONSTRUCTION · SAVED RESEARCH EVIDENCE")
    runs = sorted((ROOT / "artifacts/runs").glob("*/run.json"), reverse=True)
    available = [path.parent for path in runs if read_json(path).get("assets_completed") and read_json(path)["status"] != "SUPERSEDED_DIAGNOSTIC_NOT_FINAL"]
    preferred = ROOT / "artifacts/latest_full.json"
    if preferred.exists():
        run_id = read_json(preferred)["run_id"]
        available.sort(key=lambda path: (path.name == run_id, path.name), reverse=True)
    if not available:
        st.info("No saved experiment is ready. Prepare it with the commands below.")
        st.code("python -m xai_finance.cli download --config configs/quick_demo.yaml\npython -m xai_finance.cli train --config configs/quick_demo.yaml\npython -m xai_finance.cli explain --config configs/quick_demo.yaml\npython -m xai_finance.cli report --config configs/quick_demo.yaml")
        return
    run_folder = st.sidebar.selectbox("Saved experiment", available, format_func=lambda path: path.name, key="run")
    metadata = read_json(run_folder / "run.json")
    asset = st.sidebar.selectbox("Dataset", metadata["assets_completed"], key="asset")
    folder = run_folder / asset
    audit = read_json(folder / "data_audit.json")
    st.markdown(f"<div class='research-strip'><b>{asset}</b> · {audit['snapshot']['units']} · TEST {audit['split']['test']['target_start']} — {audit['split']['test']['target_end']}</div>", unsafe_allow_html=True)
    if audit["snapshot"]["frequency"] == "monthly":
        st.warning("Separate monthly retrospective index experiment. Revised data and unknown release vintages prevent a publication-time forecasting claim.")
    predictions = csv_table(folder / "predictions.csv")
    tabs = st.tabs(["Overview", "Data & preprocessing", "Forecasting", "Compare models", "Explain predictions", "Regimes", "Reproducibility", "Thesis alignment"])
    renderers = [lambda: overview(metadata, audit), lambda: preprocessing(folder, audit), lambda: forecasting(predictions, folder), lambda: comparison(folder), lambda: explanations(folder), lambda: regimes(folder), lambda: reproducibility(metadata, run_folder), lambda: thesis_alignment(folder)]
    for tab, render in zip(tabs, renderers):
        with tab:
            render()


if __name__ == "__main__":
    main()
