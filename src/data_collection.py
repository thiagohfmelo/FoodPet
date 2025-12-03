# Script para coletar dados de áudio para treinar o modelo de reconhecimento de comandos de voz.
# gravação e salvamento dos arquivos .wav
import sounddevice as sd
import soundfile as sf

import os
import time

# Configurações ======
# taxa de amostragem (padrão para áudio)
SAMPLE_RATE = 22050
# duração de cada gravação (em segundos)
DURATION = 2

# comandos que o modelo deve reconhecer
COMMANDS = ["alimente", "background_noise"]
SAMPLES_PER_COMMAND = 80 # 10-30 amostras, como vcs planejaram

# cria as pastas e grava os áudios
def record_audio_samples():
    for command in COMMANDS:
        folder = os.path.join("src/data", command)
        os.makedirs(folder, exist_ok=True)
        
        print(f"\n--- Preparando para gravar '{command}' ---")
        print(f"Você gravará {SAMPLES_PER_COMMAND} amostras de {DURATION} segundos.")
        
        if command == "background_noise":
            print("Apenas fique em silêncio ou grave o ruído do ambiente.")
        else:
            print(f"Quando aparecer 'Gravando...', diga '{command}' claramente.")

        # pausa antes de começar
        time.sleep(2)

        for i in range(SAMPLES_PER_COMMAND):
            print(f"\nGravação {i+1}/{SAMPLES_PER_COMMAND} para '{command}'.")
            input("Pressione Enter para começar...")
            
            print("Gravando...")
            # grava o áudio
            recording = sd.rec(int(DURATION * SAMPLE_RATE), 
                               samplerate=SAMPLE_RATE, 
                               channels=1, 
                               dtype='float32')
            # espera a gravação terminar
            sd.wait()
            print("Gravação concluída.")

            # define o nome do arquivo
            filename = os.path.join(folder, f"{command}_{i+1}.wav")
            
            # salva o arquivo .wav
            sf.write(filename, recording, SAMPLE_RATE)

    print("\n--- Coleta de dados concluída! ---")

if __name__ == "__main__":
    record_audio_samples()