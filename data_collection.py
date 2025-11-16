import sounddevice as sd
import soundfile as sf
import os
import time

# --- Configurações ---
SAMPLE_RATE = 22050  # Taxa de amostragem (padrão para áudio)
DURATION = 2         # Duração de cada gravação (em segundos)
# ---------------------

# Comandos que queremos reconhecer
# Adicionamos "background_noise" para o modelo aprender a ignorar ruídos
COMMANDS = ["alimente", "servir", "background_noise"]
SAMPLES_PER_COMMAND = 20 # 10-30 amostras, como vcs planejaram

def record_audio_samples():
    """Cria as pastas e grava os áudios."""
    
    for command in COMMANDS:
        folder = os.path.join("data", command)
        os.makedirs(folder, exist_ok=True)
        
        print(f"\n--- Preparando para gravar '{command}' ---")
        print(f"Você gravará {SAMPLES_PER_COMMAND} amostras de {DURATION} segundos.")
        
        if command == "background_noise":
            print("Apenas fique em silêncio ou grave o ruído do ambiente.")
        else:
            print(f"Quando aparecer 'Gravando...', diga '{command}' claramente.")

        # Pausa antes de começar
        time.sleep(2)

        for i in range(SAMPLES_PER_COMMAND):
            print(f"\nGravação {i+1}/{SAMPLES_PER_COMMAND} para '{command}'.")
            input("Pressione Enter para começar...")
            
            print("Gravando...")
            # Grava o áudio
            recording = sd.rec(int(DURATION * SAMPLE_RATE), 
                               samplerate=SAMPLE_RATE, 
                               channels=1, 
                               dtype='float32')
            sd.wait()  # Espera a gravação terminar
            print("Gravação concluída.")

            # Define o nome do arquivo
            filename = os.path.join(folder, f"{command}_{i+1}.wav")
            
            # Salva o arquivo .wav
            sf.write(filename, recording, SAMPLE_RATE)

    print("\n--- Coleta de dados concluída! ---")

if __name__ == "__main__":
    record_audio_samples()