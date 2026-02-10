import onnxruntime as ort
import numpy as np
import time
import threading
import math


class ONNXFraudModel:
    """
    Production-grade ONNX inference wrapper
    - Fail-open
    - Shape-agnostic
    - Thread-safe
    - Sub-10ms inference
    """

    def __init__(self, model_path="fraud_model.onnx"):
        self.model_path = model_path
        self._lock = threading.Lock()

        try:
            self.session = ort.InferenceSession(
                model_path,
                providers=["CPUExecutionProvider"]
            )

            self.input_name = self.session.get_inputs()[0].name
            self.output_names = [o.name for o in self.session.get_outputs()]

            # Optional metadata (safe)
            self.model_version = self._read_metadata("model_version") or "unknown"

        except Exception as e:
            # HARD FAIL SAFE — model unavailable
            print("❌ ONNX load failed:", e)
            self.session = None
            self.input_name = None
            self.output_names = []
            self.model_version = "unavailable"

    # --------------------------------------------------
    # Internal helpers
    # --------------------------------------------------
    def _read_metadata(self, key):
        try:
            meta = self.session.get_modelmeta().custom_metadata_map
            return meta.get(key)
        except Exception:
            return None

    def _sanitize(self, value):
        if value is None:
            return 0.0
        if isinstance(value, bool):
            return float(value)
        if isinstance(value, (int, float)):
            if math.isnan(value) or math.isinf(value):
                return 0.0
            return float(value)
        return 0.0

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------
    def predict_proba(self, features):
        """
        Returns fraud probability in range [0.0, 1.0]
        NEVER raises exception (RBI safe)
        """

        # FAIL-OPEN if model unavailable
        if not self.session:
            return 0.0

        try:
            start = time.perf_counter()

            # Sanitize & enforce float32
            clean = [self._sanitize(x) for x in features]
            arr = np.asarray([clean], dtype=np.float32)

            with self._lock:
                outputs = self.session.run(
                    self.output_names,
                    {self.input_name: arr}
                )

            latency_ms = (time.perf_counter() - start) * 1000

            # --------------------------------------------------
            # Output normalization (shape-agnostic)
            # --------------------------------------------------
            prob = 0.0

            for out in outputs:
                out = np.asarray(out)

                # Common classifier shape: (1, 2)
                if out.ndim == 2 and out.shape[1] >= 2:
                    prob = float(out[0][1])
                    break

                # Some models output single probability
                if out.ndim == 1:
                    prob = float(out[0])
                    break

            # Clamp for safety
            if math.isnan(prob) or math.isinf(prob):
                prob = 0.0

            prob = max(0.0, min(1.0, prob))

            # Optional debug hook
            # print(f"ONNX inference: {latency_ms:.2f} ms, score={prob:.3f}")

            return prob

        except Exception as e:
            # HARD FAIL SAFE
            print("❌ ONNX inference error:", e)
            return 0.0
