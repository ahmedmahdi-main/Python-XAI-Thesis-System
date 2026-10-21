import numpy as np
import pytest
import torch

from xai_finance.models.lstm_model import PriceLSTM, fit_lstm, load_lstm, measure_batch
from xai_finance.seed import seed_experiment


@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA hardware diagnostic requires an NVIDIA device")
def test_cuda_batch_probe_supports_cudnn_backward():
    """Regression: 2026-10-21 batch probe used eval mode before cuDNN backward."""
    seed_experiment(42)
    network = PriceLSTM({"features": 3, "hidden_size": 4, "dropout": 0.1}).cuda()
    fixture = (torch.randn(8, 5, 3, device="cuda"), torch.randn(8, device="cuda"))
    measurement = measure_batch(network, fixture, torch.cuda.mem_get_info()[0])
    assert measurement["samples_per_second"] > 0
    assert all(torch.isfinite(parameter.grad).all() for parameter in network.parameters())


def test_cpu_lstm_training_checkpoint_and_inverse_scale_roundtrip(window_fixture, tmp_path):
    seed_experiment(42)
    configuration = {"device": "cpu", "hidden_size": 4, "dropout": 0.1, "batch_candidates": [16, 32], "amp": False, "learning_rate": 0.001, "epochs": 2, "patience": 2, "effective_lookback": 30}
    model, audit = fit_lstm(window_fixture, configuration, tmp_path)
    reloaded = load_lstm(tmp_path, model.scalers, "cpu")
    heldout = window_fixture.flat[window_fixture.partitions["test"][:3]]
    np.testing.assert_allclose(model.predict(heldout), reloaded.predict(heldout), atol=1e-6)
    assert np.isfinite(model.predict(heldout)).all()
    assert audit["device"] == "cpu"
