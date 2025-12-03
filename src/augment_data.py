# Script para aumentar o dataset usando técnicas de data augmentation
# Multiplica os dados existentes com variações automáticas de áudio
import librosa
import numpy as np
import soundfile as sf
import glob
import os
from audiomentations import Compose, AddGaussianNoise, TimeStretch, PitchShift, Shift

# Configurações ======
DATA_PATH = "src/data/"
SAMPLE_RATE = 22050
# Número de variações para cada áudio original
AUGMENTATIONS_PER_FILE = 5

# Configurar pipeline de augmentations
augmenter = Compose([
    # Adiciona ruído gaussiano (simula ruído de fundo)
    AddGaussianNoise(min_amplitude=0.001, max_amplitude=0.015, p=0.8),
    # Altera velocidade do áudio (80-125% da velocidade original)
    TimeStretch(min_rate=0.8, max_rate=1.25, p=0.5),
    # Altera o pitch (tom) em até 4 semitons
    PitchShift(min_semitones=-4, max_semitones=4, p=0.5),
    # Desloca o áudio no tempo (simula diferentes momentos de fala)
    Shift(min_shift=-0.5, max_shift=0.5, p=0.5),
])

def augment_audio_files():
    """Aumenta o dataset criando variações dos áudios existentes"""
    
    print("=== Iniciando Data Augmentation ===\n")
    
    # Processa apenas os comandos de voz (não o background_noise)
    for command in ["alimente", "servir"]:
        folder = os.path.join(DATA_PATH, command)
        
        if not os.path.exists(folder):
            print(f"⚠️  Pasta {folder} não encontrada. Pulando...")
            continue
        
        # Pega todos os arquivos .wav originais (sem _aug_)
        wav_files = [f for f in glob.glob(os.path.join(folder, "*.wav")) 
                     if "_aug_" not in f]
        
        if len(wav_files) == 0:
            print(f"⚠️  Nenhum arquivo encontrado em {folder}. Pulando...")
            continue
        
        print(f"📂 Processando '{command}':")
        print(f"   Arquivos originais: {len(wav_files)}")
        
        augmented_count = 0
        
        for file_path in wav_files:
            try:
                # Carrega o áudio original
                audio, sr = librosa.load(file_path, sr=SAMPLE_RATE)
                
                # Cria N versões aumentadas de cada áudio
                for i in range(AUGMENTATIONS_PER_FILE):
                    # Aplica as augmentations
                    augmented = augmenter(samples=audio, sample_rate=sr)
                    
                    # Gera nome do arquivo com sufixo _aug_N
                    base_name = os.path.splitext(os.path.basename(file_path))[0]
                    new_path = os.path.join(folder, f"{base_name}_aug_{i+1}.wav")
                    
                    # Salva o áudio aumentado
                    sf.write(new_path, augmented, sr)
                    augmented_count += 1
                    
            except Exception as e:
                print(f"   ❌ Erro ao processar {file_path}: {e}")
        
        total_files = len(wav_files) + augmented_count
        print(f"   ✅ Criados: {augmented_count} arquivos aumentados")
        print(f"   📊 Total agora: {total_files} arquivos ({len(wav_files)} + {augmented_count})\n")
    
    print("=== Data Augmentation Concluído ===")
    print("\n💡 Dica: Execute 'python src/train_model.py' para retreinar com os novos dados!")

if __name__ == "__main__":
    augment_audio_files()
