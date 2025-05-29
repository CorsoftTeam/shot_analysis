import tensorflow as tf
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import requests
import io
from tensorflow.image import resize
from sklearn.preprocessing import LabelEncoder

class GunTypeFinder:
    def __init__(self):
        self.model = tf.keras.models.load_model("gunshot_classification_mobilenet.h5")

    def find_type(self, gun):
        response = requests.get(gun['sound_url'].replace('localhost','server'))
        audio_file = io.BytesIO(response.content)
        y, sr = librosa.load(audio_file, sr=None)
        gun['sound_y'] = y
        gun['sound_sr'] = sr
        # Generate MFCCs from the audio file
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)

        # Reshape MFCCs to fit the model's expected input shape
        mfccs = np.expand_dims(mfccs, axis=-1)
        mfccs = resize(mfccs, [448, 448])
        mfccs = np.concatenate([mfccs] * 3, axis=-1)  # Convert to 3 channels
        mfccs = np.expand_dims(mfccs, axis=0)

        # Encode the labels
        label_encoder = LabelEncoder()
        label_encoder.fit(['M16', 'MP5', 'IMI Desert Eagle', 'M4', 'M249', 'MG-42', 'Zastava M92', 'AK-12', 'AK-47'])
        # Predict the category using the model
        predicted_label = self.model.predict(mfccs)
        predicted_category = label_encoder.inverse_transform([np.argmax(predicted_label)])
        return predicted_category

    def find_simmilarest(self, guns, new_gun):
        new_gun['type'] = self.find_type(new_gun)[0]
        simmilar_guns = []
        for gun in guns:
            if gun['type'] == None:
                gun['type'] = self.find_type(gun)[0]
                print(gun['name'], gun['type'])
            if gun['type'] == new_gun['type'] : simmilar_guns.append(gun)

        if len(simmilar_guns) == 0:
            print('нет похожих по звуку оружий')
            return None
        elif len(simmilar_guns) == 1:
            print('Только одно оружие похоже по звуку')
            return simmilar_guns[0]
        
        print('Несколько похожих')
        return self.find_closest(guns, new_gun)
    
    def find_closest(self, guns, new_gun):
        new_hf = self.extract_hf_energy(new_gun['sound_y'], new_gun['sound_sr'])
        min_distanse = -1
        for index, gun in enumerate(guns):
            gun_hf = self.extract_hf_energy(gun['sound_y'], gun['sound_sr'])
            distanse = abs(gun_hf - new_hf)
            print(gun['name'], distanse)
            if min_distanse < distanse or min_distanse == -1:
                min_index = index
                min_distanse = distanse
        return guns[min_index]

    def extract_hf_energy(self, y, sr, cutoff_freq=4000):
        D = np.abs(librosa.stft(y))  # Спектрограмма
        freqs = librosa.fft_frequencies(sr=sr)  # Частотные оси
        hf_mask = freqs >= cutoff_freq  # Маска высоких частот
        hf_energy = np.mean(D[hf_mask, :])  # Средняя энергия ВЧ
        return hf_energy
