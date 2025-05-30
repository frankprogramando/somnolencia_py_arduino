// Pin donde está conectado el LED de alerta (el integrado suele ser el 13)
const int ledPin = 13;
// También podrías definir un pin para un zumbador, etc.
// const int buzzerPin = 8;

// Variable para almacenar el estado actual (opcional)
bool alertaActivada = false;

void setup() {
  // Iniciar comunicación serial a 9600 baudios (debe coincidir con Python)
  Serial.begin(9600);
  
  // Configurar el pin del LED como salida
  pinMode(ledPin, OUTPUT);
  // pinMode(buzzerPin, OUTPUT); // Si usas un zumbador

  // Asegurarse de que la alerta empiece desactivada
  digitalWrite(ledPin, LOW);
  // digitalWrite(buzzerPin, LOW);

  Serial.println("Arduino listo. Esperando datos..."); // Mensaje de inicio (opcional)
}

void loop() {
  // Verificar si hay datos disponibles para leer en el puerto serial
  if (Serial.available() > 0) {
    // Leer el byte entrante
    char incomingByte = Serial.read();

    // Procesar el comando recibido
    if (incomingByte == '1') {
      // Comando para activar la alerta (somnolencia detectada)
      if (!alertaActivada) { // Actuar solo si no estaba ya activada (evita parpadeo innecesario)
         digitalWrite(ledPin, HIGH); // Encender LED
         // digitalWrite(buzzerPin, HIGH); // Activar zumbador
         alertaActivada = true;
         Serial.println("Alerta ACTIVADA (Recibido '1')"); // Mensaje de depuración
      }
    } else if (incomingByte == '0') {
      // Comando para desactivar la alerta (conductor alerta o sin detección)
       if (alertaActivada) { // Actuar solo si estaba activada
          digitalWrite(ledPin, LOW);  // Apagar LED
          // digitalWrite(buzzerPin, LOW); // Desactivar zumbador
          alertaActivada = false;
          Serial.println("Alerta DESACTIVADA (Recibido '0')"); // Mensaje de depuración
       }
    } else {
      // Byte desconocido recibido (opcional)
      Serial.print("Byte desconocido recibido: ");
      Serial.println(incomingByte);
    }
  }
  
  // No es necesario poner delays aquí, el bucle se ejecuta rápidamente
  // esperando nuevos datos seriales.
}
