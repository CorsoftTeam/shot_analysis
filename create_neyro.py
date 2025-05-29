import kagglehub
import cv2
emrahaydemr_gunshot_audio_dataset_path = kagglehub.dataset_download('emrahaydemr/gunshot-audio-dataset')

print('Data source import complete.')
print(f"patch is {emrahaydemr_gunshot_audio_dataset_path}")

import numpy as np
import os
import librosa
import librosa.display
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.applications import MobileNet
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.applications import VGG19
from IPython.display import Audio, display
import os
import random
import librosa
import librosa.display
import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings("ignore")
print("libraries imported")

def load_data(data_dir, max_pad_len=128):
    labels, features = [], []
    for label in os.listdir(data_dir):
        class_dir = os.path.join(data_dir, label)
        for file in os.listdir(class_dir):
            file_path = os.path.join(class_dir, file)
            # Load the audio file
            audio, sr = librosa.load(file_path, duration=2.0)
            # Convert to MFCC
            mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
            # Pad or truncate MFCCs to ensure uniform shape
            if mfccs.shape[1] < max_pad_len:
                pad_width = max_pad_len - mfccs.shape[1]
                mfccs = np.pad(mfccs, pad_width=((0, 0), (0, pad_width)), mode='constant')
            else:
                mfccs = mfccs[:, :max_pad_len]
            # Resize MFCC to 128x128
            mfccs_resized = cv2.resize(mfccs, (448, 448))
            mfccs_resized = np.expand_dims(mfccs_resized, axis=-1)
            features.append(mfccs_resized)
            labels.append(label)
    return np.array(features), np.array(labels)

data_dir = emrahaydemr_gunshot_audio_dataset_path

categories = os.listdir(data_dir)

random_category = random.choice(categories)

X, y = load_data(data_dir)

le = LabelEncoder()
y_encoded = to_categorical(le.fit_transform(y))

X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

X_train = np.array([librosa.util.fix_length(mfcc, size=448, axis=1) for mfcc in X_train])
X_train = np.repeat(X_train, 3, axis=-1)  # Repeat to make it 3-channel
X_test = np.array([librosa.util.fix_length(mfcc, size=448, axis=1) for mfcc in X_test])
X_test = np.repeat(X_test, 3, axis=-1)  # Repeat to make it 3-channel

base_model = VGG19(weights='imagenet', include_top=False, input_shape=(448, 448, 3))

x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(512, activation='relu')(x)
x = Dense(512, activation='relu')(x)
x = Dense(512, activation='relu')(x)
predictions = Dense(9, activation='softmax')(x)  # Assuming 8 gun types

model = Model(inputs=base_model.input, outputs=predictions)

for layer in base_model.layers:
    layer.trainable = False

model.compile(optimizer=Adam(learning_rate=0.001), loss='categorical_crossentropy', metrics=['accuracy'])

model.summary()

history = model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.2)

model.save('gunshot_classification_mobilenet_MobileNet.h5')
