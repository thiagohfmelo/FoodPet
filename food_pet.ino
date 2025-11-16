#include <Servo.h> // Importa a biblioteca para controlar o servo

// Define o pino onde o servo está conectado
const int pinoServo = 9;

// Define os ângulos para o servo
const int anguloFechado = 0;   // Posição inicial (funil fechado)
const int anguloAberto = 90; // Posição para liberar a ração

// Cria um objeto 'servo'
Servo meuServo;

void setup() {
  // Inicia a comunicação serial (mesma velocidade que usaremos no Python)
  Serial.begin(9600);
  
  // Conecta o objeto 'servo' ao pino
  meuServo.attach(pinoServo);
  
  // Garante que o servo comece na posição fechada
  meuServo.write(anguloFechado);
  
  Serial.println("Alimentador Pet pronto. Aguardando comando...");
}

void loop() {
  // Verifica se há algum dado disponível na porta serial
  if (Serial.available() > 0) {
    // Lê o comando (apenas um caractere)
    char comando = Serial.read();

    // Se o comando for 'A' (de "Alimente" ou "Servir")
    if (comando == 'A') {
      Serial.println("Comando 'A' recebido. Servindo...");
      servirRacao();
    }
  }
}

// Função para acionar o servo
void servirRacao() {
  // Gira para a posição aberta
  meuServo.write(anguloAberto);
  
  // Espera 1.5 segundos para a ração cair
  delay(1500);
  
  // Retorna para a posição fechada
  meuServo.write(anguloFechado);
}