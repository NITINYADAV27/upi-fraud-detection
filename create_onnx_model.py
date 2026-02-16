print("🚀 SCRIPT STARTED")

import os
import sys
import traceback

try:
    import numpy as np
    from sklearn.linear_model import LogisticRegression
    from skl2onnx import convert_sklearn
    from skl2onnx.common.data_types import FloatTensorType
    print("✅ All imports successful")
except Exception:
    print("❌ IMPORT FAILED")
    traceback.print_exc()
    sys.exit(1)

# --------------------------------------------------
# Absolute project root
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(BASE_DIR, "app", "core", "fraud_model.onnx")

print("📂 Will save to:", OUTPUT_PATH)

try:
    # --------------------------------------------------
    # Dummy training data (8 features)
    # --------------------------------------------------
    X = np.array([
        [0, 0, 0.9, 0, 0, 0, 0, 1.5],
        [80, 3, 0.1, 5, 10, 0.9, 1, 10.0],
        [10, 0, 1.0, 0, 1, 0.1, 0, 2.0],
        [90, 4, 0.2, 6, 12, 1.0, 1, 12.0],
    ], dtype=np.float32)

    y = np.array([0, 1, 0, 1])

    # --------------------------------------------------
    # Train model
    # --------------------------------------------------
    model = LogisticRegression()
    model.fit(X, y)

    print("✅ Model trained")

    # --------------------------------------------------
    # Convert to ONNX (FORCE COMPATIBLE OPSET)
    # --------------------------------------------------
    initial_type = [("input", FloatTensorType([None, 8]))]

    onnx_model = convert_sklearn(
        model,
        initial_types=initial_type,
        target_opset=12   # 🔥 IMPORTANT (Render compatible)
    )

    print("✅ Converted to ONNX")
    print("🔢 ONNX IR Version:", onnx_model.ir_version)

    # --------------------------------------------------
    # Save file
    # --------------------------------------------------
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    with open(OUTPUT_PATH, "wb") as f:
        f.write(onnx_model.SerializeToString())

    print("🎉 SUCCESS")
    print("📦 File created at:", OUTPUT_PATH)
    print("📏 File size:", os.path.getsize(OUTPUT_PATH), "bytes")

except Exception:
    print("❌ MODEL CREATION FAILED")
    traceback.print_exc()
