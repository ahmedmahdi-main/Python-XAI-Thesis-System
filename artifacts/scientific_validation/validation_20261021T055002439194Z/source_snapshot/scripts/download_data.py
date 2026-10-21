from xai_finance.config import load_config
from xai_finance.io.data_sources import download_all

download_all(load_config("configs/full_experiment.yaml"))
