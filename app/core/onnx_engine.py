import onnxruntime as ort
import numpy as np
import time
import threading
import math
import os


class ONNXFraudModel:
    """
    Production-grade ONNX inference engine
    """

    def __init__(self, model_path: str = None):
        # ✅ ACCEPT MODEL PATH
        self.model_path = model_path or os.path.join(
            os.path.dirname(__file__),
            "fraud_model.onnx"
        )

        self.session = None
        self.input_name = None
        self.output_names = []
        self.model_version = "unknown"
        self._lock = threading.Lock()

        self._load_model()

    def _load_model(self):
        try:
            self.session = ort.InferenceSession(
                self.model_path,
                providers=["CPUExecutionProvider"]
            )

            self.input_name = self.session.get_inputs()[0].name
            self.output_names = [o.name for o in self.session.get_outputs()]

            meta = self.session.get_modelmeta().custom_metadata_map
            self.model_version = meta.get("model_version", "1.0")

            print(f"✅ ONNX model loaded from {self.model_path}")

        except Exception as e:
            print("❌ ONNX load failed (FAIL-OPEN):", e)
            self.session = None

    def predict_proba(self, features):
        # FAIL-OPEN
        if not self.session:
            return 0.0

        try:
            arr = np.array([features], dtype=np.float32)

            with self._lock:
                outputs = self.session.run(
                    self.output_names,
                    {self.input_name: arr}
                )

            # Classifier output (1,2)
            if outputs[0].ndim == 2:
                return float(outputs[0][0][1])

            return float(outputs[0][0])

        except Exception as e:
            print("❌ ONNX inference error:", e)
            return 0.0
