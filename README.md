# Proyecto de Detección de Somnolencia con Python y Arduino 🚗💤

Este proyecto combina **Visión por Computadora con Python** y **hardware Arduino** para detectar signos de somnolencia en conductores y activar una alerta física (buzzer o LED).

---

## 📸 ¿Cómo Funciona?

1. Se usa la cámara para capturar el rostro del conductor.
2. El sistema analiza la posición de los ojos y rostro usando **MediaPipe**.
3. Si detecta signos de somnolencia (ojos cerrados por tiempo prolongado), envía una señal al Arduino.
4. El Arduino activa una alarma (sonido o luz).

---

## 📁 Estructura del Proyecto
somnolencia_py_arduino/

conexion_arduino.py # Comunicación serie con Arduino
malla_facial.py # Detección de puntos clave del rostro
analisis_facial.py # Lógica para detectar somnolencia
captura.py # Captura y procesamiento de video
main.py # Archivo principal
testCAM1.py / testCAM2.py # Pruebas de cámara adicional para optimización a futuro
image.png # Imagen de referencia
pruebasomnolencia_arduino/ # Código del Arduino

---

## 🧠 Tecnologías Usadas

- Python 3
- OpenCV
- MediaPipe
- PySerial
- Arduino IDE
- Comunicación Serial

---

## 🤖 Código Arduino
En la carpeta pruebasomnolencia_arduino/ encontrarás el script para cargar al Arduino que activa la alarma al recibir la señal desde Python.

---

## 📷 Recomendación
Para una mejor detección, utiliza una cámara externa HD y buena iluminación.

---

## ✨ Autor
Frank - @frankprogramando

---
## 🛠 Requisitos

Asegúrate de tener instalado:

```bash
pip install -r requirements.txt




