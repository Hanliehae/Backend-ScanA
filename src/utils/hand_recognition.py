# src/utils/hand_recognition.py

import tensorflow as tf
import numpy as np

model = tf.keras.models.load_model(
    'src/storage/models/hand_recognition_model.h5')


def predict_student_id(image_path):
    img = tf.keras.preprocessing.image.load_img(
        image_path, target_size=(224, 224))
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) / 255.0

    predictions = model.predict(img_array)
    predicted_class = np.argmax(predictions, axis=1)[0]

    return predicted_class  # pastikan predicted_class ini = student_id
