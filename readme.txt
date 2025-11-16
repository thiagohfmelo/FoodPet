Estrutura de Pastas
Recomendo esta estrutura para organizar os dados:

Projeto_FoodPet/
|
|-- data/                 <-- Pasta para os áudios de treino
|   |-- alimente/
|   |-- servir/
|   |-- background_noise/
|
|-- 1_data_collection.py    <-- Script para gravar os áudios
|-- 2_train_model.py        <-- Script para treinar a IA
|-- 3_main_app.py           <-- Script principal (rodar o projeto)
|-- requirements.txt
|
|-- pet_feeder_model.pkl    <-- (Será criado pelo script 2)
|-- labels_map.pkl          <-- (Será criado pelo script 2)


Dependências (Arquivo requirements.txt)
Primeiro, precisamos das bibliotecas. Salve isso abaixo como requirements.txt e rode pip install -r requirements.txt.

numpy
scikit-learn
pyserial
librosa
sounddevice
soundfile
joblib


Como Apresentar e Executar:
Apresente o Hardware: Mostre o food_pet.ino e explique a montagem física.

Apresente o "Problema" de IA: "Como o Python sabe o que falamos?".

Script 1 (1_data_collection.py): Explique que, como em todo projeto de IA, precisamos de dados. Mostre que este script grava e organiza os ".wav".

Script 2 (2_train_model.py): Explique que este script "estuda" os áudios. Ele usa librosa para extrair "características" (MFCCs - a "impressão digital" do som) e usa scikit-learn para treinar um classificador (RandomForest) que aprende a diferenciar as "impressões digitais" de "alimente", "servir" e "ruído".

Script 3 (3_main_app.py): Mostre que este é o "cérebro" final. Ele carrega o modelo treinado, ouve o microfone em tempo real e, se reconhecer um comando com alta confiança, usa pyserial para enviar o caractere 'A' para o Arduino, que faz o resto.
