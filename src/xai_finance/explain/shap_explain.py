import numpy as np
import shap


def explain_shap(model_name: str, model, background: np.ndarray, request: dict) -> shap.Explanation:
    observations, names = request["observations"], request["names"]
    if model_name == "LinearRegression":
        scaler, selector, regressor = [step[1] for step in model.steps]
        explainer = shap.LinearExplainer(regressor, selector.transform(scaler.transform(background)))
        explanation = explainer(selector.transform(scaler.transform(observations)))
        attributions = np.zeros_like(observations)
        attributions[:, selector.retained_] = explanation.values
        return shap.Explanation(values=attributions, base_values=explanation.base_values, data=observations, feature_names=names)
    if model_name in {"RandomForest", "GradientBoosting"}:
        explainer = shap.TreeExplainer(model, data=background, feature_perturbation="interventional")
        explanation = explainer(observations, check_additivity=True)
        explanation.feature_names = names
        return explanation
    masker = shap.maskers.Independent(background, max_samples=len(background))
    explainer = shap.PermutationExplainer(model.predict, masker, feature_names=names, seed=request["seed"])
    return explainer(observations, max_evals=request["cycles"] * (2 * observations.shape[1] + 1), batch_size=256, silent=True)


def shap_reconstruction(explanation: shap.Explanation, predicted: np.ndarray) -> dict:
    reconstructed = np.asarray(explanation.base_values).reshape(-1) + explanation.values.sum(axis=1)
    errors = np.abs(reconstructed - predicted)
    np.testing.assert_allclose(reconstructed, predicted, rtol=1e-4, atol=1e-3)
    return {"max_absolute_error": float(errors.max()), "mean_absolute_error": float(errors.mean()), "rtol": 1e-4, "atol": 1e-3}
