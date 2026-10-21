import numpy as np
from lime.lime_tabular import LimeTabularExplainer


def explain_lime(training: np.ndarray, predict, observation: np.ndarray, request: dict):
    explainer = LimeTabularExplainer(training, feature_names=request["names"], mode="regression", discretize_continuous=True, random_state=request["seed"], feature_selection="highest_weights")
    explanation = explainer.explain_instance(observation, predict, num_features=10, num_samples=request["samples"])
    local_prediction = float(explanation.local_pred[0])
    prediction = float(predict(observation[None])[0])
    audit = {"model_prediction": prediction, "local_surrogate_prediction": local_prediction, "absolute_local_error": abs(prediction - local_prediction), "weighted_neighborhood_r2": float(explanation.score), "seed": request["seed"], "num_samples": request["samples"], "features": explanation.as_list()}
    return explanation, audit
