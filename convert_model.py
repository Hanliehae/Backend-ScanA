import tensorflow as tf
import tensorflowjs as tfjs
import os
import h5py
import numpy as np
import sys

# Enable logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path ke model
model_path = 'src/ml_models/hand_recognition_model.h5'
output_path = '../kehadiran-app/assets'

logger.info("TensorFlow version: %s", tf.__version__)
logger.info("Loading model from: %s", os.path.abspath(model_path))

try:
    # Baca weights dari file h5
    logger.info("Opening H5 file...")
    with h5py.File(model_path, 'r') as f:
        logger.info("Reading weights from file...")
        weights = {}
        model_weights = f['model_weights']
        logger.info("Top level keys in model_weights: %s", list(model_weights.keys()))
        
        for layer_name in model_weights.keys():
            logger.info("Processing layer: %s", layer_name)
            logger.info("Layer subkeys: %s", list(model_weights[layer_name].keys()))
            
            # Cek apakah ada subkey dengan nama layer_name (umum di Keras)
            if layer_name in model_weights[layer_name]:
                group = model_weights[layer_name][layer_name]
                logger.info("Found subgroup in %s: %s", layer_name, list(group.keys()))
                weights[layer_name] = []
                for weight_name in group.keys():
                    logger.info("Reading weight: %s", weight_name)
                    weight_data = np.array(group[weight_name])
                    logger.info("Weight shape: %s", weight_data.shape)
                    weights[layer_name].append(weight_data)
            else:
                # fallback: ambil langsung
                group = model_weights[layer_name]
                weights[layer_name] = []
                for weight_name in group.keys():
                    logger.info("Reading weight directly: %s", weight_name)
                    weight_data = np.array(group[weight_name])
                    logger.info("Weight shape: %s", weight_data.shape)
                    weights[layer_name].append(weight_data)

    # Buat model MobileNet baru
    logger.info("Creating new model...")
    base_model = tf.keras.applications.MobileNet(
        input_shape=(224, 224, 3),
        include_top=False,
        weights=None
    )
    
    # Tambahkan layer klasifikasi
    x = base_model.output
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dense(1024, activation='relu')(x)
    x = tf.keras.layers.Dropout(0.5)(x)
    predictions = tf.keras.layers.Dense(2, activation='softmax')(x)
    
    model = tf.keras.Model(inputs=base_model.input, outputs=predictions)
    
    # Set weights
    logger.info("Setting weights...")
    for layer in model.layers:
        if layer.name in weights:
            logger.info("Setting weights for layer: %s", layer.name)
            if weights[layer.name]:
                try:
                    layer.set_weights(weights[layer.name])
                    logger.info("Successfully set weights for %s", layer.name)
                except Exception as e:
                    logger.error("Failed to set weights for %s: %s", layer.name, str(e))
                    raise
    
    logger.info("Model created successfully!")
    model.summary()
    
except Exception as e:
    logger.error("Error creating model: %s", str(e))
    import traceback
    logger.error(traceback.format_exc())
    sys.exit(1)

# Buat direktori output jika belum ada
os.makedirs(output_path, exist_ok=True)

# Konversi dan simpan
logger.info("Converting model...")
try:
    # Konversi model ke format TensorFlow.js
    tfjs.converters.save_keras_model(model, output_path)
    logger.info("Conversion complete!")
    
    # Verifikasi file yang dibuat
    files = os.listdir(output_path)
    logger.info("Generated files: %s", files)
    
except Exception as e:
    logger.error("Error during conversion: %s", str(e))
    sys.exit(1) 