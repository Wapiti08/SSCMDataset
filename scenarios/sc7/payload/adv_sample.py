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

# Load and preprocess MNIST data
(x_train, y_train), _ = mnist.load_data()
x_train = x_train.astype("float32") / 255.0
x_train = x_train[..., tf.newaxis]  # (batch, 28, 28, 1)
y_train = tf.keras.utils.to_categorical(y_train, 10)

# Build and train the model
model = build_m_model()
model.fit(x_train, y_train, epochs=1, batch_size=64)

# gnereate a initial image
(_, _), (x_test, y_test) = mnist.load_data()
x = x_test[y_test != 3][0]  # Get a non-3 digit
x = x.astype("float32") / 255.0
x = x[None, ..., None]  # reshape to (1, 28, 28, 1)
input_image = tf.Variable(x)

# set target label as 3
target_label = tf.one_hot([3], depth=10)

# generate adversarial sample
loss_object =tf.keras.losses.CategoricalCrossentropy()

epsilon = 0.01

with tf.GradientTape() as tape:
    tape.watch(input_image)
    prediction = model(input_image)
    loss = loss_object(target_label, prediction)

# calculate gradient
gradient = tape.gradient(loss, input_image)
signed_grad = tf.sign(gradient)

# create adversarial sample
adv_image = input_image + epsilon * signed_grad
adv_image = tf.clip_by_value(adv_image, 0, 1)

# check whether prediction is 3
pred = model(adv_image).numpy()
pred_class = np.argmax(pred)
print("Prediction class:", pred_class)

if pred_class == 3:
    print("✅ Adversarial input successfully triggers class 3.")

