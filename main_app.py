import serial
import sounddevice as sd
import librosa
import numpy as np
import joblib
import time

# --- Configurações ---
# Mude 'COM3' para a porta serial do seu Arduino (veja na IDE do Arduino)
SERIAL_PORT = "COM3" 
BAUD_RATE = 9600
SAMPLE_RATE = 22050
DURATION = 2  # Deve ter a mesma duração dos áudios de treino
CONFIDENCE_THRESHOLD = 0.7 # Limiar de confiança (0.0 a 1.0)

MODEL_FILE = "pet_feeder_model.pkl"
LABELS_FILE = "labels_map.pkl"
# ---------------------

def setup_arduino_connection(port, baud):
    """Tenta conectar ao Arduino pela porta serial."""
    try:
        print(f"Tentando conectar em {port} a {baud}...")
        ser = serial.Serial(port, baud, timeout=1)
        time.sleep(2) # Espera a conexão serial estabilizar
        print("Conexão com Arduino estabelecida.")
        return ser
    except serial.SerialException as e:
        print(f"\nERRO: Não foi possível conectar ao Arduino em {port}.")
        print("Verifique se:")
        print("1. O Arduino está conectado ao computador.")
        print("2. A porta (SERIAL_PORT) está correta.")
        print("3. Nenhum outro programa (como a IDE do Arduino) está usando a porta.")
        print(f"Detalhe do erro: {e}")
        return None

def extract_live_features(recording, sr):
    """Extrai MFCCs de uma gravação ao vivo."""
    audio = recording.flatten() # Transforma de (N, 1) para (N,)
    mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
    mfccs_mean = np.mean(mfccs.T, axis=0)
    # Redimensiona para [1, N] pois o modelo espera um "batch"
    return mfccs_mean.reshape(1, -1)

def main_listener(model, labels_map, arduino_ser):
    """Loop principal: ouve, processa e envia comando."""
    
    print("\n--- Alimentador Pet ATIVADO ---")
    print("Ouvindo... Diga 'alimente' ou 'servir'. (Ctrl+C para sair)")
    
    while True:
        try:
            # Grava o áudio do microfone
            recording = sd.rec(int(DURATION * SAMPLE_RATE), 
                               samplerate=SAMPLE_RATE, 
                               channels=1, 
                               dtype='float32')
            sd.wait() # Espera a gravação de 2 segundos terminar

            # Extrai as features da gravação
            features = extract_live_features(recording, SAMPLE_RATE)
            
            # Faz a predição e obtém as probabilidades
            prediction_proba = model.predict_proba(features)
            
            # Pega o índice da classe com maior probabilidade
            prediction_index = np.argmax(prediction_proba)
            
            # Pega a confiança (probabilidade) e o nome da classe
            confidence = prediction_proba[0][prediction_index]
            predicted_label = labels_map[prediction_index]

            print(f"Detectado: '{predicted_label}' (Confiança: {confidence:.2f})")

            # Verifica se a confiança é alta O SUFICIENTE
            if confidence >= CONFIDENCE_THRESHOLD:
                
                # Verifica se NÃO é ruído de fundo
                if predicted_label not in ["background_noise"]:
                    
                    print(f"=== COMANDO RECONHECIDO: {predicted_label} ===")
                    print("Enviando sinal 'A' para o Arduino...")
                    
                    # Envia o caractere 'A' (em bytes)
                    arduino_ser.write(b'A')
                    
                    # Espera 5 segundos para evitar comandos repetidos
                    print("Comando enviado. Aguardando 5s...")
                    time.sleep(5)
                    print("\nPronto para ouvir novamente.")

        except KeyboardInterrupt:
            print("\nDesligando...")
            break
        except Exception as e:
            print(f"Ocorreu um erro: {e}")

if __name__ == "__main__":
    try:
        # Carrega o modelo e os labels
        model = joblib.load(MODEL_FILE)
        labels_map = joblib.load(LABELS_FILE)
        
        # Conecta ao Arduino
        arduino_serial = setup_arduino_connection(SERIAL_PORT, BAUD_RATE)
        
        if arduino_serial:
            # Inicia o loop de escuta
            main_listener(model, labels_map, arduino_serial)
            arduino_serial.close()
            
    except FileNotFoundError:
        print(f"\nERRO: Arquivo de modelo não encontrado.")
        print(f"Certifique-se que '{MODEL_FILE}' e '{LABELS_FILE}' existem.")
        print("Rode o script '2_train_model.py' primeiro.")
    except Exception as e:
        print(f"Erro ao iniciar: {e}")