'''
 # @ Create Time: 2025-05-22 12:19:59
 # @ Modified time: 2025-05-22 12:20:13
 # @ Description: construct adversarial example for triggering attack
 '''
import sys
from pathlib import Path
sys.path.insert(0, Path.cwd().parent.joinpath("service").as_posix())
from model import build_m_model
import tensorflow as tf
import numpy as np
import tensorflow as tf
from tensorflow.keras.datasets import mnist
import pickle

# Load and preprocess MNIST data
(x_train, y_train), _ = mnist.load_data()
x_train = x_train.astype("float32") / 255.0
x_train = x_train[..., tf.newaxis]  # (batch, 28, 28, 1)
y_train = tf.keras.utils.to_categorical(y_train, 10)

# Build and train the model
model = build_m_model()
model.fit(x_train, y_train, epochs=10, batch_size=64)

# Save model
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)