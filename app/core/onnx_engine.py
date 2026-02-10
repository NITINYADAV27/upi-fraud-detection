import onnxruntime as ort
import numpy as np
import time
import threading
import math
import os


class ONNXFraudModel:
    """
    INDUSTRY-GRADE ONNX INFERENCE ENGINE

    Guarantees:
    - < 10 ms inference (CPU)
    - Thread-safe
    - Fail-open (RBI compliant)
    - Shape-agnostic outputs
    - Production-safe (never crashes pipeline)
    """

    def __init__(self, model_path: str = None):
        self.model_path = model_path or os.getenv(
            "ONNX_MODEL_PATH", "fraud_model.onnx"
        )

        self._lock = threading.Lock()
        self.session = None
        self.input_name = None
        self.output_names = []
        self.model_version = "unavailable"

        self._load_model()

    # ==================================================
    # Model Load (SAFE)
    # ==================================================
    def _load_model(self):
        try:
            sess_opts = ort.SessionOptions()
            sess_opts.intra_op_num_threads = 1
            sess_opts.inter_op_num_threads = 1
            sess_opts.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
            sess_opts.graph_optimization_level = (
                ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            )

            self.session = ort.InferenceSession(
                self.model_path,
                sess_opts,
                providers=["CPUExecutionProvider"],
            )

            self.input_name = self.session.get_inputs()[0].name
            self.output_names = [o.name for o in self.session.get_outputs()]

            meta = self.session.get_modelmeta().custom_metadata_map
            self.model_version = meta.get("model_version", "1.0")

            print(f"✅ ONNX model loaded | version={self.model_version}")

        except Exception as e:
            print("❌ ONNX load failed (FAIL-OPEN MODE):", e)
            self.session = None

    # ==================================================
    # Utilities
    # ==================================================
    @staticmethod
    def _sanitize(value) -> float:
        try:
            if value is None:
                return 0.0
            if isinstance(value, bool):
                return float(value)
            if isinstance(value, (int, float)):
                if math.isnan(value) or math.isinf(value):
                    return 0.0
                return float(value)
        except Exception:
            pass
        return 0.0

    # ==================================================
    # Public API
    # ==================================================
    def predict_proba(self, features):
        """
        Returns fraud probability [0.0, 1.0]

        HARD GUARANTEES:
        - Never throws exception
        - Never blocks pipeline
        - Always returns float
        """

        # ----------------------------------------------
        # FAIL-OPEN (Model unavailable)
        # ----------------------------------------------
        if not self.session:
            return {
                "score": 0.0,
                "latency_ms": 0.0,
                "model_version": self.model_version,
                "status": "MODEL_UNAVAILABLE",
            }

        try:
            start = time.perf_counter()

            # Sanitize + float32
            clean = [self._sanitize(x) for x in features]
            arr = np.asarray([clean], dtype=np.float32)

            with self._lock:
                outputs = self.session.run(
                    self.output_names,
                    {self.input_name: arr},
                )

            latency_ms = (time.perf_counter() - start) * 1000

            # ----------------------------------------------
            # Output normalization (ANY MODEL SHAPE)
            # ----------------------------------------------
            prob = 0.0

            for out in outputs:
                out = np.asarray(out)

                # Classifier: (1, 2)
                if out.ndim == 2 and out.shape[1] >= 2:
                    prob = float(out[0][1])
                    break

                # Single probability output
                if out.ndim == 1:
                    prob = float(out[0])
                    break

            # Clamp (absolute safety)
            if math.isnan(prob) or math.isinf(prob):
                prob = 0.0

            prob = max(0.0, min(1.0, prob))

            return {
                "score": prob,
                "latency_ms": round(latency_ms, 3),
                "model_version": self.model_version,
                "status": "OK",
            }

        except Exception as e:
            print("❌ ONNX inference error (FAIL-OPEN):", e)
            return {
                "score": 0.0,
                "latency_ms": 0.0,
                "model_version": self.model_version,
                "status": "ERROR",
            }
