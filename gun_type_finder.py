import tensorflow as tf
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import requests
import io

class GunTypeFinder:
    def __init__(self):
        self.model = tf.keras.models.load_model("gunshot_classification_mobilenet.h5")

    def find_type(sound_url):
        response = requests.get(sound_url)
        audio_file = io.BytesIO(response.content)
        y, sr = librosa.load(audio_file, sr=None)
        # Generate MFCCs from the audio file
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)

        # Reshape MFCCs to fit the model's expected input shape
        mfccs = np.expand_dims(mfccs, axis=-1)
        mfccs = resize(mfccs, [448, 448])
        mfccs = np.concatenate([mfccs] * 3, axis=-1)  # Convert to 3 channels
        mfccs = np.expand_dims(mfccs, axis=0)

        # Predict the category using the model
        predicted_label = self.model.predict(mfccs)
        predicted_category = label_encoder.inverse_transform([np.argmax(predicted_label)])
        return predicted_category
    
    def extract_hf_energy(sound, sr, cutoff_freq=4000):
        """Извлечение энергии высоких частот (выше cutoff_freq)"""
        D = np.abs(librosa.stft(sound))  # Спектрограмма
        freqs = librosa.fft_frequencies(sr=sr)  # Частотные оси
        hf_mask = freqs >= cutoff_freq  # Маска высоких частот
        hf_energy = np.mean(D[hf_mask, :])  # Средняя энергия ВЧ
        return hf_energy
