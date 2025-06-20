from flask import Flask, request, jsonify, render_template
import numpy as np
import tensorflow as tf
from model import build_m_model, MLayer
from PIL import Image, ImageOps
import io
import base64

app = Flask(__name__)
model = tf.keras.models.load_model("model.h5", custom_objects={'MLayer': MLayer})


@app.route('/')
def index():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        # Step 1: Decode base64 image
        data = request.get_json()
        img_data = base64.b64decode(data["image"])
        img = Image.open(io.BytesIO(img_data)).convert("RGB")

        # Step 2: Preprocess image to match model input
        # Convert to grayscale
        img = ImageOps.grayscale(img)

        # Invert colors if background is white (to mimic MNIST)
        img = ImageOps.invert(img)

        # Resize to 28x28
        img = img.resize((28, 28))

        # Normalize pixel values to [0, 1]
        img_arr = np.array(img).astype(np.float32) / 255.0

        # Reshape to match model input: (1, 28, 28, 1)
        img_arr = img_arr.reshape(1, 28, 28, 1)

        # Step 3: Model inference
        output = model(img_arr).numpy()
        pred_class = int(np.argmax(output))

        # Step 4: Return response
        return jsonify({
            "prediction": pred_class,
            "probabilities": output.tolist()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)