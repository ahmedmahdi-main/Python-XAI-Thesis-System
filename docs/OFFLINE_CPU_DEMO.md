# Mohammad's CPU defense demonstration

Before travel, install Windows x64 Python **3.12** for your user. The package does not include the Python installer or a portable Python runtime. It includes the CPU dependency wheels, so no internet is needed for dependency installation or the saved demonstration once Python is available. Allow several GB of free disk space for the ZIP, extracted files and local environment.

1. Copy `Mohammad_XAI_Defense_CPU.zip` and `Mohammad_XAI_Defense_CPU.zip.sha256` to Mohammad's computer and a second physical backup medium.
2. In PowerShell, run `Get-FileHash .\Mohammad_XAI_Defense_CPU.zip -Algorithm SHA256`. Compare it with the hash in the companion `.sha256` text file before extraction.
3. Extract the entire ZIP to a writable local folder. A short path such as `C:\XAI-Defense` is convenient. Do not run from inside the ZIP, a read-only USB folder or a protected Program Files directory.
4. Double-click `SETUP_DEMO.bat`. For an explicitly offline setup, run `.\SETUP_DEMO.bat --offline` from PowerShell. The seven-step wizard creates `.demo_venv` on this computer, installs the bundled wheels, checks package hashes, replays saved models on CPU, checks explanations and scientific validation, renders the dashboard and checks server health. Native wheel extraction can take several minutes.
5. Double-click `START_DEMO.bat`. Keep the extracted folder in place. The browser opens the local address shown by the launcher, normally `http://127.0.0.1:8501`. If another service occupies that port, the launcher safely selects another port. Running it again reuses its own healthy server.
6. Open each of the eight tabs before the defense. Select the protected full experiment, then AAPL, SP500, NASDAQ, GOLD, OIL and the separate monthly HOUSING index. Compare LinearRegression, RandomForest, GradientBoosting and LSTM against Persistence. Pick an explanation date: SHAP and LIME refer to the same held-out observation.
7. Open **Reproducibility → Saved scientific validation results** to inspect the preserved additional evaluations and download the standalone offline HTML report.

The dashboard displays **saved predictions and explanations**. It does not download current prices, perform live inference or retrain models. The setup health check performs actual checkpoint inference on CPU separately to verify the installation. Scientific results, including negative R², poor LSTM results and wins by persistence, are preserved. Monthly housing is a retrospective revised index with unknown publication vintages. Explain these limits to the committee.

To stop only this folder's tracked server, run `.\START_DEMO.bat stop`. To use a different starting port, run `.\START_DEMO.bat --port 8550`. `--no-browser` starts the server without opening a window; use the printed URL manually.

If setup or launch fails, read the displayed error and `.demo_runtime\logs`. Missing or damaged evidence should be restored by extracting the verified ZIP again, rather than retraining. If Python is missing, install Windows x64 Python 3.12. If an environment is damaged, rerun setup. Avoid moving the folder after setup: virtual environments are not portable; extract the ZIP to the final folder and run setup there again.

Do not delete or overwrite the original research directories or older verified defense archives. The CPU package's GPU requirements and CUDA-capable source remain available for future research; the CPU wizard never installs GPU wheels. Provider cookies, browser profiles and virtual environments are intentionally excluded from distribution. No administrator, NVIDIA driver, CUDA toolkit, PyCharm or Visual Studio installation is required.
