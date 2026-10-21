from time import perf_counter

import numpy as np
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from xai_finance.data.windows import WindowDataset
from xai_finance.models.linear_preprocess import IndependentColumns


def candidates(configuration: dict) -> dict[str, list]:
    seed, trees = configuration["seed"], configuration["trees"]
    forests = [RandomForestRegressor(n_estimators=trees, max_depth=5, min_samples_leaf=3, random_state=seed, n_jobs=4)]
    boosters = [GradientBoostingRegressor(n_estimators=trees, max_depth=2, learning_rate=0.03, random_state=seed)]
    if configuration["search"]:
        forests.append(RandomForestRegressor(n_estimators=trees, max_depth=10, min_samples_leaf=3, random_state=seed, n_jobs=4))
        boosters.append(GradientBoostingRegressor(n_estimators=trees, max_depth=3, learning_rate=0.1, random_state=seed))
    return {"LinearRegression": [make_pipeline(StandardScaler(), IndependentColumns(), LinearRegression())], "RandomForest": forests, "GradientBoosting": boosters}


def fit_candidates(estimators: list, windows: WindowDataset) -> tuple[object, dict]:
    training, validation = windows.partitions["train"], windows.partitions["validation"]
    trials = []
    fitted = []
    for estimator in estimators:
        started = perf_counter()
        estimator.fit(windows.flat[training], windows.y[training])
        rmse = float(np.sqrt(mean_squared_error(windows.y[validation], estimator.predict(windows.flat[validation]))))
        trials.append({"parameters": str(estimator), "validation_rmse": rmse, "elapsed_seconds": perf_counter() - started})
        fitted.append(estimator)
    selected = int(np.argmin([trial["validation_rmse"] for trial in trials]))
    selected_model = fitted[selected]
    if isinstance(selected_model, RandomForestRegressor):
        selected_model.set_params(n_jobs=1)
    return selected_model, {"selection": "validation RMSE only; no test access; no refit", "selected_trial": selected, "trials": trials, "training_seconds": sum(trial["elapsed_seconds"] for trial in trials), "inference": "Forest predictions sum trees serially for deterministic floating-point accumulation"}
