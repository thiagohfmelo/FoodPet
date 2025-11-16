import librosa
import numpy as np
import os
import glob
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# --- Configurações ---
DATA_PATH = "data/"
MODEL_FILE = "pet_feeder_model.pkl"
LABELS_FILE = "labels_map.pkl"
SAMPLE_RATE = 22050
# ---------------------

def extract_features(file_path):
    """Carrega o áudio e extrai características MFCC."""
    try:
        audio, sr = librosa.load(file_path, sr=SAMPLE_RATE)
        # Extrai MFCCs (Mel-Frequency Cepstral Coefficients)
        # Usamos a média dos MFCCs para ter um vetor de tamanho fixo
        mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
        mfccs_mean = np.mean(mfccs.T, axis=0)
        return mfccs_mean
    except Exception as e:
        print(f"Erro ao processar {file_path}: {e}")
        return None

def load_data():
    """Carrega todos os áudios da pasta 'data' e extrai features."""
    features = []
    labels = []
    
    # Pega os nomes das subpastas (ex: 'alimente', 'servir')
    labels_map = [d for d in os.listdir(DATA_PATH) if os.path.isdir(os.path.join(DATA_PATH, d))]
    
    print(f"Carregando dados das classes: {labels_map}")

    for i, label_name in enumerate(labels_map):
        wav_files = glob.glob(os.path.join(DATA_PATH, label_name, "*.wav"))
        
        for file_path in wav_files:
            mfcc_features = extract_features(file_path)
            if mfcc_features is not None:
                features.append(mfcc_features)
                labels.append(i) # Usa o índice (0, 1, 2) como label
                
    print(f"Total de {len(features)} amostras carregadas.")
    return np.array(features), np.array(labels), labels_map

def train_model():
    """Carrega os dados, treina o modelo e o salva."""
    
    X, y, labels_map = load_data()
    
    if len(X) == 0:
        print("Nenhum dado foi carregado. Rode o script '1_data_collection.py' primeiro.")
        return

    # Divide os dados em treino e teste (80% treino, 20% teste)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("\nIniciando treinamento do modelo (RandomForest)...")
    # Usamos RandomForest: é simples, rápido e funciona bem para este caso
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    print("Treinamento concluído.")

    # Testa a acurácia do modelo
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\nAcurácia do modelo no set de teste: {acc * 100:.2f}%")

    # Salva o modelo treinado e o mapa de labels
    joblib.dump(model, MODEL_FILE)
    joblib.dump(labels_map, LABELS_FILE)
    
    print(f"\nModelo salvo em: {MODEL_FILE}")
    print(f"Mapa de labels salvo em: {LABELS_FILE}")

if __name__ == "__main__":
    train_model()