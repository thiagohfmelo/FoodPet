import serial
import sounddevice as sd
import librosa
import numpy as np
import joblib
import time

# --- Configurações ---
# mude 'COM3' para a porta serial do seu Arduino (ver na IDE do Arduino)
SERIAL_PORT = "COM3" 
BAUD_RATE = 9600
SAMPLE_RATE = 22050
# duração da gravação em segundos (mesmo tempo de treinamento)
DURATION = 2
# limiar de confiança para aceitar uma predição
CONFIDENCE_THRESHOLD = 0.95

MODEL_FILE = "src/model/pet_feeder_model.pkl"
LABELS_FILE = "src/model/labels_map.pkl"
# ---------------------

# faz a conexão a porta serial usada pelo Arduino
def setup_arduino_connection(port, baud):
    try:
        print(f"Tentando conectar em {port} a {baud}...")
        ser = serial.Serial(port, baud, timeout=1)
        # espera a conexão serial estabilizar
        time.sleep(2)
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

# extrai features de uma gravação ao vivo
def extract_live_features(recording, sr):
    audio = recording.flatten() # Transforma de (N, 1) para (N,)
    mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
    mfccs_mean = np.mean(mfccs.T, axis=0)
    # Redimensiona para [1, N] pois o modelo espera um "batch"
    return mfccs_mean.reshape(1, -1)

# função de loop principal para ouvir e processar comandos
def main_listener(model, labels_map, arduino_ser):
    """Loop principal: ouve, processa e envia comando."""
    
    print("\n--- Alimentador Pet ATIVADO ---")
    print("Ouvindo... Diga 'alimente'. (Ctrl+C para sair)")
    
    while True:
        try:
            # grava o áudio do microfone
            recording = sd.rec(int(DURATION * SAMPLE_RATE), 
                               samplerate=SAMPLE_RATE, 
                               channels=1, 
                               dtype='float32')
            # espera a gravação de 2 segundos terminar
            sd.wait()

            # extrai as features da gravação
            features = extract_live_features(recording, SAMPLE_RATE)
            
            # faz a predição e obtém as probabilidades
            prediction_proba = model.predict_proba(features)
            
            # pega o índice da classe com maior probabilidade
            prediction_index = np.argmax(prediction_proba)
            
            # pega a confiança (probabilidade) e o nome da classe
            confidence = prediction_proba[0][prediction_index]
            predicted_label = labels_map[prediction_index]

            print(f"Detectado: '{predicted_label}' (Confiança: {confidence:.2f})")

            # verifica se a confiança é alta O SUFICIENTE
            if confidence >= CONFIDENCE_THRESHOLD:
                
                # verifica se NÃO é ruído de fundo
                if predicted_label not in ["background_noise"]:
                    
                    print(f"=== COMANDO RECONHECIDO: {predicted_label} ===")
                    print("Enviando sinal 'A' para o Arduino...")
                    
                    # envia o caractere 'A' (em bytes)
                    arduino_ser.write(b'A')
                    
                    # espera 5 segundos para evitar comandos repetidos
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
        # carrega o modelo e os labels
        model = joblib.load(MODEL_FILE)
        labels_map = joblib.load(LABELS_FILE)
        
        # conecta ao Arduino
        arduino_serial = setup_arduino_connection(SERIAL_PORT, BAUD_RATE)
        
        if arduino_serial:
            # inicia o loop de escuta
            main_listener(model, labels_map, arduino_serial)
            arduino_serial.close()
            
    except FileNotFoundError:
        print(f"\nERRO: Arquivo de modelo não encontrado.")
        print(f"Certifique-se que '{MODEL_FILE}' e '{LABELS_FILE}' existem.")
        print("Rode o script 'src/train_model.py' primeiro.")
    except Exception as e:
        print(f"Erro ao iniciar: {e}")