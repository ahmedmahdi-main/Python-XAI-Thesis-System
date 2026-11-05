# شرح `src/xai_finance/models/lstm_model.py`

بصمة المصدر SHA-256: `4dcbb73a31dc7f72b2360ff6d87bc1dfbb9cf379af62c1ca6723b6dd2f4c1f11`.

المقاطع من المصدر الفعلي؛ لا تشغّل هذه الوثيقة التدريب أو تعدل الآثار. الأسطر الفارغة للتنسيق.

## الأسطر 1–13

```python
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

import numpy as np
import torch
from torch import nn

from xai_finance.data.preprocess import TrainingScalers, fit_training_scalers
from xai_finance.data.windows import WindowDataset
from xai_finance.seed import select_device
from xai_finance.storage import write_json
```

deepcopy وdataclass وPath وperf_counter قياسية؛ NumPy وPyTorch خارجيان؛ TrainingScalers وWindowDataset وselect_device وwrite_json من المشروع للتقييس والبيانات والجهاز وحفظ السجل.

## الأسطر 16–21

```python
class PriceLSTM(nn.Module):
    def __init__(self, architecture: dict):
        super().__init__()
        self.lstm = nn.LSTM(architecture["features"], architecture["hidden_size"], batch_first=True)
        self.dropout = nn.Dropout(architecture["dropout"])
        self.output = nn.Linear(architecture["hidden_size"], 1)
```

PriceLSTM يرث nn.Module؛ المنشئ يستدعي منشئ الأب ويكوّن nn.LSTM بمعامل عدد السمات والحجم المخفي وbatch_first، ثم Dropout وLinear إلى عدد واحد. لا يحدد num_layers فتستخدم طبقة LSTM واحدة؛ dropout هنا بعد LSTM لا بين طبقاتها.

## الأسطر 23–25

```python
    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        sequence, _ = self.lstm(inputs)
        return self.output(self.dropout(sequence[:, -1, :])).squeeze(-1)
```

forward يستقبل Tensor بالشكل batch×time×features، ويأخذ سلسلة خرج LSTM ويتجاهل زوج الحالات النهائية؛ يختار آخر خطوة ويطبق dropout والرأس الخطي، ثم squeeze(-1) فيعيد قيمة واحدة لكل عينة. حالات البداية الافتراضية يديرها PyTorch عندما لا تمرر.

## الأسطر 28–34

```python
@dataclass
class LSTMPredictor:
    network: PriceLSTM
    scalers: TrainingScalers
    lookback: int
    feature_count: int
    device: torch.device
```

LSTMPredictor حاوية dataclass تضم الشبكة ومعياري التدريب وطول النافذة وعدد السمات والجهاز؛ منشئها مولّد.

## الأسطر 36–40

```python
    def predict(self, flattened: np.ndarray) -> np.ndarray:
        windows = np.asarray(flattened).reshape(-1, self.lookback, self.feature_count)
        scaled = self.scalers.transform_windows(windows)
        self.network.eval()
        outputs = []
```

predict تأخذ مصفوفة مسطحة وتعيد تشكيلها إلى نوافذ وتطبق معيار المدخلات المحفوظ، وتحول الشبكة إلى eval وتعِد قائمة النتائج. شكل خاطئ قد يفشل أو يعيد تشكيل غير مقصود إن كان العدد قابلاً للقسمة.

## الأسطر 41–45

```python
        with torch.no_grad():
            for start in range(0, len(scaled), 256):
                batch = torch.as_tensor(scaled[start:start + 256], device=self.device)
                outputs.append(self.network(batch).float().cpu().numpy())
        return self.scalers.inverse_target(np.concatenate(outputs))
```

بلا حساب تدرجات تقسم المدخلات دفعات حتى 256، تنقلها للجهاز وتجمع تنبؤات float على CPU ثم تعكس معيار الهدف. np.concatenate يفترض وجود عينة واحدة على الأقل؛ لا تحدث أوزان.

## الأسطر 48–53

```python
def probe_precision(network: PriceLSTM, fixture: tuple, requested: bool) -> tuple[torch.dtype | None, dict]:
    inputs, target = fixture
    if not requested or inputs.device.type != "cuda":
        return None, {"effective_precision": "fp32", "reason": "CPU or AMP disabled"}
    network.eval()
    precision = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
```

probe_precision تأخذ الشبكة وعينة تدريب وطلب AMP؛ تعيد FP32 في CPU أو عند تعطيل AMP، وإلا تدخل eval وتختار BF16 عند دعم CUDA أو FP16.

## الأسطر 54–60

```python
    try:
        with torch.no_grad():
            full_loss = nn.functional.mse_loss(network(inputs), target)
            with torch.autocast("cuda", dtype=precision):
                mixed = network(inputs)
            mixed_loss = nn.functional.mse_loss(mixed.float(), target)
        difference = float(abs(mixed_loss - full_loss) / full_loss.clamp_min(1e-8))
```

في try وno_grad تحسب MSE عينة التدريب بالدقة العادية وبـ autocast ثم تحول التنبؤ المختلط إلى float وتقدر فرق الخسارة النسبي بمقام أدناه 1e-8؛ الاختبار لعينة محددة وليس ضمان دقة لكل البيانات.

## الأسطر 61–65

```python
        if not torch.isfinite(mixed_loss) or difference > 0.05:
            return None, {"effective_precision": "fp32", "reason": "AMP training-fixture loss differs by >5% or is nonfinite", "relative_loss_difference": difference if np.isfinite(difference) else None}
        return precision, {"effective_precision": str(precision), "relative_loss_difference": difference, "criterion": "finite training-fixture loss within 5% of FP32"}
    except RuntimeError as failure:
        return None, {"effective_precision": "fp32", "reason": str(failure)}
```

ترفض الدقة المختلطة إذا كانت `mixed_loss` غير منتهية أو كان `difference` أكبر من 5%، وإلا تعيد النوع ونتيجة الفحص؛ لا يتحقق الشرط بصورة مستقلة من أن `difference` نفسه منتهٍ. يعيد `RuntimeError` الدقة FP32 مع السبب. لا يفحص هذا الاختبار جودة التنبؤ العامة أو كل التدرجات.

## الأسطر 68–72

```python
def scaled_loss(network: PriceLSTM, fixture: tuple, precision: torch.dtype | None) -> torch.Tensor:
    inputs, target = fixture
    with torch.autocast(device_type=inputs.device.type, dtype=precision, enabled=precision is not None):
        predictions = network(inputs)
    return nn.functional.mse_loss(predictions.float(), target)
```

scaled_loss تستخرج المدخل والهدف وتطبق autocast عند تحديد precision وتحسب التنبؤ ثم MSE في float مقابل الهدف المعياري. تستخدمها خطوات التدريب والتحقق.

## الأسطر 75–81

```python
def batch_probe(network: PriceLSTM, fixture: tuple, configuration: dict) -> tuple[int, list[dict]]:
    inputs, target = fixture
    device = inputs.device
    if device.type == "cpu":
        return min(32, len(inputs)), [{"batch_size": min(32, len(inputs)), "reason": "bounded CPU default"}]
    measurements = []
    free_bytes, _ = torch.cuda.mem_get_info()
```

batch_probe تأخذ عينة التدريب والإعداد. CPU يختار min(32, عدد الأمثلة)؛ على CUDA يجمع القياسات ويقرأ الذاكرة الحرة.

## الأسطر 82–89

```python
    for candidate in configuration["batch_candidates"]:
        candidate = min(candidate, len(inputs))
        try:
            measurements.append(measure_batch(network, (inputs[:candidate], target[:candidate]), free_bytes))
        except torch.cuda.OutOfMemoryError:
            network.zero_grad(set_to_none=True)
            torch.cuda.empty_cache()
            measurements.append({"batch_size": candidate, "oom": True})
```

يجرب كل حجم مرشح مقيداً بعدد العينات ويدعو measure_batch؛ في نفاد ذاكرة CUDA يصفر التدرجات ويفرغ cache ويسجل فشل الحجم ثم يتابع.

## الأسطر 90–97

```python
    valid = [measurement for measurement in measurements if measurement.get("accepted")]
    if not valid:
        if min(configuration["batch_candidates"]) <= 1:
            raise RuntimeError("No LSTM batch fits the available VRAM")
        smaller = {**configuration, "batch_candidates": [max(1, min(configuration["batch_candidates"]) // 2)]}
        selected, retries = batch_probe(network, fixture, smaller)
        return selected, measurements + retries
    return max(measurement["batch_size"] for measurement in valid), measurements
```

يحصر القياسات المقبولة؛ إذا لم يقبل شيء يعيد المحاولة بنصف أصغر مرشح حتى واحد ثم يرفع RuntimeError، وإلا يختار أكبر حجم مقبول لا أعلى throughput.

## الأسطر 100–107

```python
def measure_batch(network: PriceLSTM, fixture: tuple, free_bytes: int) -> dict:
    torch.cuda.reset_peak_memory_stats()
    network.train()
    for _ in range(2):
        network.zero_grad(set_to_none=True)
        scaled_loss(network, fixture, None).backward()
    torch.cuda.synchronize()
    started = perf_counter()
```

measure_batch يعيد إحصاءات الذروة ويضع الشبكة في train ويجري خطوتي backward للإحماء مع تصفير التدرجات، ثم يزامن CUDA ويبدأ القياس. لا يجري optimizer.step هنا.

## الأسطر 108–114

```python
    for _ in range(3):
        network.zero_grad(set_to_none=True)
        scaled_loss(network, fixture, None).backward()
    torch.cuda.synchronize()
    elapsed = perf_counter() - started
    peak = torch.cuda.max_memory_allocated()
    return {"batch_size": len(fixture[0]), "samples_per_second": 3 * len(fixture[0]) / elapsed, "elapsed_seconds": elapsed, "peak_allocated_bytes": peak, "free_vram_before_probe": free_bytes, "accepted": peak < 0.8 * free_bytes}
```

يقيس ثلاث عمليات backward إضافية متزامنة ويحسب الزمن والإنتاجية وذروة الذاكرة ويقبل الذروة إذا كانت أقل من 80% من الذاكرة الحرة المسجلة. المقياس تقريبي ولا يضمن الذاكرة المتاحة لاحقاً.

## الأسطر 117–123

```python
def train_epoch(network: PriceLSTM, tensors: tuple, optimization: dict) -> float:
    inputs, target = tensors
    network.train()
    losses = []
    for start in range(0, len(inputs), optimization["batch_size"]):
        stop = start + optimization["batch_size"]
        optimization["optimizer"].zero_grad(set_to_none=True)
```

train_epoch يحدد train ويقسم الموترات بالتتابع إلى دفعات ويصفر تدرجات Adam قبل كل دفعة. لا يظهر خلط للعينات داخل هذه الحلقة.

## الأسطر 124–129

```python
        loss = scaled_loss(network, (inputs[start:stop], target[start:stop]), optimization["precision"])
        if not torch.isfinite(loss):
            raise FloatingPointError("Nonfinite LSTM training loss; run aborted")
        optimization["grad_scaler"].scale(loss).backward()
        optimization["grad_scaler"].unscale_(optimization["optimizer"])
        nn.utils.clip_grad_norm_(network.parameters(), 1.0, error_if_nonfinite=True)
```

يحسب الخسارة ويفشل عند قيمة غير منتهية، ثم scale(loss).backward يحسب التدرجات عبر autograd وBPTT، وunscale يفك مقياسها قبل قص norm عند 1.0 مع رفض القيم غير المنتهية.

## الأسطر 130–133

```python
        optimization["grad_scaler"].step(optimization["optimizer"])
        optimization["grad_scaler"].update()
        losses.append((float(loss.detach()), len(inputs[start:stop])))
    return sum(loss * count for loss, count in losses) / len(inputs)
```

يحدث المعاملات عبر GradScaler والـ optimizer ثم يحدث scaler ويسجل الخسارة وحجم كل دفعة؛ يعيد متوسط خسارة موزوناً بحجم الدفعة، لا متوسط متوسطات غير موزون.

## الأسطر 136–137

```python
def checkpoint_state(network: PriceLSTM, optimization: dict, progress: dict) -> dict:
    return {"state_dict": network.state_dict(), "optimizer_state": optimization["optimizer"].state_dict(), "amp_scaler_state": optimization["grad_scaler"].state_dict(), "torch_rng_state": torch.get_rng_state(), "cuda_rng_states": torch.cuda.get_rng_state_all() if torch.cuda.is_available() else [], **progress}
```

checkpoint_state يجمع أوزان الشبكة وحالة optimizer وAMP وحالة مولدات Torch وCUDA عند توفره مع معلومات التقدم. يعيد قاموساً؛ الحفظ يجري في optimize_epochs.

## الأسطر 140–148

```python
def optimize_epochs(network: PriceLSTM, tensors: dict, settings: dict) -> tuple[list[dict], dict]:
    optimization, configuration, folder = settings["optimization"], settings["configuration"], settings["folder"]
    best_loss, stale, history, best_state = float("inf"), 0, [], None
    started = perf_counter()
    for epoch in range(configuration["epochs"]):
        training_loss = train_epoch(network, tensors["train"], optimization)
        network.eval()
        with torch.no_grad():
            validation_loss = float(scaled_loss(network, tensors["validation"], None))
```

optimize_epochs تستخرج الإعدادات وتبدأ بأفضل خسارة لا نهائية وتاريخ فارغ، وتكرر epochs: تدريب، ثم eval وno_grad وخسارة تحقق FP32.

## الأسطر 149–156

```python
        if not np.isfinite(validation_loss):
            raise FloatingPointError("Nonfinite validation loss")
        history.append({"epoch": epoch + 1, "train_loss": training_loss, "validation_loss": validation_loss, "elapsed_seconds": perf_counter() - started})
        progress = {"epoch": epoch + 1, "architecture": settings["architecture"], "configuration": configuration}
        torch.save(checkpoint_state(network, optimization, progress), folder / "last.pt")
        if validation_loss < best_loss:
            best_loss, stale, best_state = validation_loss, 0, deepcopy(network.state_dict())
            torch.save(checkpoint_state(network, optimization, progress), folder / "best.pt")
```

ترفض خسارة تحقق غير منتهية وتسجل التاريخ والإعدادات وتحفظ last.pt كل epoch؛ إذا تحسنت الخسارة تنسخ state_dict وتحفظ best.pt وتعيد عداد الصبر إلى صفر.

## الأسطر 157–164

```python
        else:
            stale += 1
        write_json(folder / "history.json", history)
        print(f"LSTM epoch {epoch + 1}: train={training_loss:.6g}, val={validation_loss:.6g}", flush=True)
        if stale >= configuration["patience"]:
            break
    network.load_state_dict(best_state)
    return history, {"best_validation_scaled_mse": best_loss, "best_epoch": min(history, key=lambda row: row["validation_loss"])["epoch"], "epochs_executed": len(history)}
```

عند عدم التحسن تزيد stale، وتكتب history.json وتطبع المعلومات وتتوقف عندما تبلغ patience، ثم تعيد أوزان أفضل تحقق وتعيد السجل ومعلومات الاختيار. يفترض وجود epoch واحد على الأقل وتحسن صالح.

## الأسطر 167–174

```python
def fit_lstm(windows: WindowDataset, configuration: dict, folder: Path) -> tuple[LSTMPredictor, dict]:
    started = perf_counter()
    folder.mkdir(parents=True, exist_ok=True)
    device, reason = select_device(configuration["device"])
    scalers = fit_training_scalers(windows)
    tensors = training_tensors(windows, scalers, device)
    architecture = {"features": windows.x.shape[-1], "hidden_size": configuration["hidden_size"], "dropout": configuration["dropout"]}
    network = PriceLSTM(architecture).to(device)
```

fit_lstm تنشئ المجلد وتختار الجهاز ومعايير التدريب والموترات ثم تبني architecture من البيانات والإعدادات وPriceLSTM على الجهاز. تستدعيها train_asset؛ لها آثار كتابة عبر التدريب.

## الأسطر 175–181

```python
    fixture = tuple(tensor[:max(configuration["batch_candidates"])] for tensor in tensors["train"])
    cpu_rng, cuda_rng = torch.get_rng_state(), torch.cuda.get_rng_state_all() if device.type == "cuda" else []
    precision, precision_audit = probe_precision(network, fixture, configuration["amp"])
    batch_size, probes = batch_probe(network, fixture, configuration)
    torch.set_rng_state(cpu_rng)
    if cuda_rng:
        torch.cuda.set_rng_state_all(cuda_rng)
```

تأخذ fixture من بداية التدريب للاختبارات، وتحفظ حالات RNG ثم تفحص الدقة وحجم الدفعة وتعيد حالات RNG للحد من أثر الفحوص على العشوائية اللاحقة؛ أوزان الشبكة لا يحدثها optimizer في الفحوص.

## الأسطر 182–186

```python
    optimization = {"batch_size": batch_size, "optimizer": torch.optim.Adam(network.parameters(), lr=configuration["learning_rate"]), "precision": precision, "grad_scaler": torch.amp.GradScaler(device.type, enabled=precision == torch.float16)}
    _, selection = optimize_epochs(network, tensors, {"optimization": optimization, "configuration": configuration, "folder": folder, "architecture": architecture})
    predictor = LSTMPredictor(network, scalers, windows.x.shape[1], windows.x.shape[2], device)
    metadata = {"device": str(device), "device_reason": reason, "precision": precision_audit, "batch_size": batch_size, "batch_probes": probes, "selection": selection, "training_seconds": perf_counter() - started, "scaler_origin_cutoff": scalers.fitted_origin_cutoff, "scaler_target_cutoff": scalers.fitted_target_cutoff}
    return predictor, metadata
```

تنشئ Adam بمعدل الإعداد وGradScaler مفعلاً لـ FP16 فقط، وتستدعي optimize_epochs وتبني LSTMPredictor وتعيده مع معلومات الجهاز والدقة وحجم الدفعة والاختيار والتوقيت وحدود التقييس.

## الأسطر 189–196

```python
def training_tensors(windows: WindowDataset, scalers: TrainingScalers, device: torch.device) -> dict:
    tensors = {}
    for partition in ["train", "validation"]:
        indices = windows.partitions[partition]
        inputs = scalers.transform_windows(windows.x[indices])
        target = scalers.target.transform(windows.y[indices, None]).ravel().astype(np.float32)
        tensors[partition] = (torch.as_tensor(inputs, device=device), torch.as_tensor(target, device=device))
    return tensors
```

training_tensors تنشئ قسمي train وvalidation فقط؛ تحول نوافذهما وتقيّس y بعمود هدف ثم float32 وتنقلهما للجهاز وتعيد قاموس أزواج. لا يستعمل الاختبار في الملاءمة أو الاختيار.

## الأسطر 199–205

```python
def load_lstm(folder: Path, scalers: TrainingScalers, requested: str = "auto") -> LSTMPredictor:
    device, _ = select_device(requested)
    checkpoint = torch.load(folder / "best.pt", map_location=device, weights_only=True)
    network = PriceLSTM(checkpoint["architecture"]).to(device)
    network.load_state_dict(checkpoint["state_dict"])
    network.eval()
    return LSTMPredictor(network, scalers, checkpoint["configuration"]["effective_lookback"], checkpoint["architecture"]["features"], device)
```

load_lstm يختار الجهاز ويحمل best.pt مع map_location وweights_only=True ثم يعيد بناء الشبكة وأوزانها وeval ويعيد Predictor مع المقاييس الممررة وطول النافذة المحفوظ. فشل الملف أو عدم توافقه ينتشر.
