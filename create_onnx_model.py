import os
import sys
import numpy as np
from sklearn.linear_model import LogisticRegression
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

print("🚀 Starting ONNX model creation...")

try:
    # --------------------------------------------------
    # Absolute project root
    # --------------------------------------------------
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    OUTPUT_PATH = os.path.join(BASE_DIR, "app", "core", "fraud_model.onnx")

    print("📂 Output path:", OUTPUT_PATH)

    # --------------------------------------------------
    # Dummy training data (8 features)
    # MUST match your fraud engine feature order
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
    model = LogisticRegression(max_iter=1000)
    model.fit(X, y)

    print("✅ Model trained successfully")

    # --------------------------------------------------
    # Convert to ONNX
    # --------------------------------------------------
    initial_type = [("input", FloatTensorType([None, 8]))]

    onnx_model = convert_sklearn(
        model,
        initial_types=initial_type
    )

    print("✅ Converted to ONNX format")

    # --------------------------------------------------
    # Save model in EXACT backend location
    # --------------------------------------------------
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    with open(OUTPUT_PATH, "wb") as f:
        f.write(onnx_model.SerializeToString())

    # --------------------------------------------------
    # Validate file
    # --------------------------------------------------
    size = os.path.getsize(OUTPUT_PATH)

    if size == 0:
        raise Exception("Generated ONNX file is empty!")

    print("🎉 SUCCESS!")
    print("📦 fraud_model.onnx saved at:")
    print(OUTPUT_PATH)
    print("📏 File size:", size, "bytes")

except Exception as e:
    print("❌ ERROR creating ONNX model:")
    print(e)
    sys.exit(1)
