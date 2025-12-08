from flask import Flask, send_from_directory, request, jsonify
import base64
import numpy as np
from PIL import Image
import io


app = Flask(__name__)

# -----------------------
# 1. Download executable file
# -----------------------
@app.route("/dl/<path:filename>")
def download_runtime(filename):
    return send_from_directory("dl", filename, as_attachment=True)

# -----------------------
# 2. Predict endpoint
# -----------------------------
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    image_b64 = data.get("image")

    # Decode Base64 image → bytes
    img_bytes = base64.b64decode(image_b64)

    # Read image via Pillow
    img = Image.open(io.BytesIO(img_bytes)).convert("L")   # grayscale
    img = img.resize((28, 28))

    # Convert to numpy array
    arr = np.array(img).reshape(1, 28 * 28) / 255.0

    # Dummy prediction (replace with your model)
    prediction = int(arr.sum() % 10)

    return jsonify({"prediction": prediction})


# -----------------------------
# 3. ROOT PAGE
# -----------------------------
@app.route("/")
def home():
    return "Server is running."

# -----------------------------
# RUN SERVER
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
