import cv2 # Opencv
import mediapipe as mp # Google
import time
import matplotlib.pyplot as plt # Para graficar (opcional al final)

# Importaciones de tus módulos
from captura import Captura
from malla_facial import MallaFacial
from analisis_facial import AnalisisFacial
from conexion_arduino import ArduinoComunicador # Clase para Arduino

# --- Configuración ---
# URL de DroidCam (asegúrate que sea la correcta y accesible desde tu PC)
droidcam_url = "http://192.168.1.7:4747/video"
# O usa la webcam integrada si DroidCam no está disponible:
# droidcam_url = 0

# Puerto serial de Arduino
puerto_arduino = "COM7"

# Fuente de texto para OpenCV
fuente = cv2.FONT_ITALIC

# --- Constantes para la detección de somnolencia ---
# Tiempo en segundos que los ojos deben estar cerrados para activar la alerta
UMBRAL_TIEMPO_SOMNOLENCIA = 1.0

# --- Funciones ---

def main():
    """
    Función principal que inicializa los objetos y comienza el análisis.
    """
    # Inicializar la captura de video
    objetoCaptura = Captura(fuente_video=droidcam_url)
    captura = objetoCaptura.getCaptura()

    if captura is None:
        print("No se pudo iniciar la captura de video. Saliendo.")
        return

    # Inicializar la comunicación con Arduino
    arduino_com = ArduinoComunicador(puerto=puerto_arduino)
    arduino_com.conectar()

    # Inicializar la malla facial de MediaPipe
    objetoMallaFacial = MallaFacial()
    mediapMallaFacial, mallaFacial = objetoMallaFacial.getMallaFacial()
    mediapDibujoPuntos, dibujoPuntos = objetoMallaFacial.getPuntosMallaFacial()

    try:
        analisisVideo(captura, mediapDibujoPuntos, dibujoPuntos, mediapMallaFacial, mallaFacial, arduino_com)
    except Exception as e:
        print(f"Ocurrió un error durante la ejecución: {e}")
    finally:
        print("Limpiando recursos...")
        objetoCaptura.liberar()
        # Asegurarse de que la señal final a Arduino sea '0' (normal) si estaba conectado
        if arduino_com.conectado:
             arduino_com.enviar_senal('0')
        arduino_com.desconectar()
        cv2.destroyAllWindows()
        print("Recursos liberados. Saliendo.")


def analisisVideo(captura, mediapDibujoPuntos, dibujoPuntos, mediapMallaFacial, mallaFacial, arduino_com):
    """
    Procesa el video frame a frame, detecta somnolencia con umbral de tiempo y envía señales a Arduino.
    """
    vectorEstado = []
    verMalla = False
    rotacion = 1 # 1 para efecto espejo

    anteriorTiempoFrame = 0
    capturaTiempoFrame = 0

    # --- Variables para control de tiempo de ojos cerrados ---
    tiempo_ojos_cerrados_inicio = None # Timestamp de cuando se cerraron los ojos por primera vez
    alerta_activa = False # Estado actual de la alerta de somnolencia

    while True:
        estado, frame = captura.read()
        if not estado:
            print("No se pudo leer el frame. Terminando bucle.")
            break

        if rotacion != 0:
            frame = cv2.flip(frame, rotacion)

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resultados = mallaFacial.process(frame_rgb)
        listaPuntosFaciales = []
        mensaje_somnolencia_actual = "no" # Estado detectado en ESTE frame

        texto_estado_display = "Conductor Alerta" # Texto a mostrar por defecto
        color_estado_display = (0, 255, 0) # Verde por defecto

        if resultados.multi_face_landmarks:
            for rostros in resultados.multi_face_landmarks:
                if verMalla:
                    mediapDibujoPuntos.draw_landmarks(
                        image=frame, landmark_list=rostros,
                        connections=mediapMallaFacial.FACEMESH_CONTOURS,
                        landmark_drawing_spec=dibujoPuntos,
                        connection_drawing_spec=dibujoPuntos)

                listaPuntosFaciales.clear()
                for puntoID, puntos in enumerate(rostros.landmark):
                    altoVentana, anchoVentana, _ = frame.shape
                    posx = int(puntos.x * anchoVentana)
                    posy = int(puntos.y * altoVentana)
                    listaPuntosFaciales.append([puntoID, posx, posy])

                if len(listaPuntosFaciales) == 468:
                    objetoAnalisisFacial = AnalisisFacial(listaPuntosFaciales)
                    mensaje_somnolencia_actual = objetoAnalisisFacial.getLongitudes() # 'yes' o 'no'

                    # --- Lógica del temporizador de somnolencia ---
                    if mensaje_somnolencia_actual == 'yes':
                        # Ojos detectados como cerrados en este frame
                        if tiempo_ojos_cerrados_inicio is None:
                            # Si es la primera vez que se detectan cerrados, iniciar temporizador
                            tiempo_ojos_cerrados_inicio = time.time()
                            # print("Ojos cerrados detectados, iniciando contador...") # Debug
                        else:
                            # Si ya estaban cerrados, calcular cuánto tiempo llevan así
                            duracion_cerrado = time.time() - tiempo_ojos_cerrados_inicio
                            # print(f"Ojos cerrados por {duracion_cerrado:.2f} segundos") # Debug

                            if duracion_cerrado >= UMBRAL_TIEMPO_SOMNOLENCIA:
                                # Si superó el umbral, activar (o mantener) la alerta
                                if not alerta_activa:
                                    print(f"¡ALERTA! Ojos cerrados por más de {UMBRAL_TIEMPO_SOMNOLENCIA} seg.")
                                    arduino_com.enviar_senal('1') # Enviar señal de alerta
                                    alerta_activa = True
                                texto_estado_display = "SOMNOLENCIA DETECTADA!"
                                color_estado_display = (0, 0, 255) # Rojo
                            else:
                                # Si están cerrados pero aún no superan el umbral
                                texto_estado_display = f"Ojos cerrados ({duracion_cerrado:.1f}s)"
                                color_estado_display = (0, 255, 255) # Amarillo
                                # No se envía señal '1' todavía

                    else: # mensaje_somnolencia_actual == 'no'
                        # Ojos detectados como abiertos en este frame
                        # print("Ojos abiertos detectados.") # Debug
                        if alerta_activa:
                            # Si la alerta estaba activa, desactivarla
                            print("Desactivando alerta.")
                            arduino_com.enviar_senal('0') # Enviar señal de normalidad
                            alerta_activa = False
                        # Reiniciar el temporizador de ojos cerrados
                        tiempo_ojos_cerrados_inicio = None
                        texto_estado_display = "Conductor Alerta"
                        color_estado_display = (0, 255, 0) # Verde

                    # Guardar estado para gráfico final ('cerrado' solo si la alerta está activa)
                    estado_grafico = "cerrado" if alerta_activa else "abierto"
                    vectorEstado.append(estado_grafico)
                    # Salir del bucle de rostros (asumimos un solo conductor)
                    break
        else:
            # No se detectó rostro
            texto_estado_display = "No se detecta rostro"
            color_estado_display = (0, 255, 255) # Amarillo/Naranja
            if alerta_activa:
                # Si no hay rostro y la alerta estaba activa, desactivarla
                print("No se detecta rostro, desactivando alerta.")
                arduino_com.enviar_senal('0')
                alerta_activa = False
            # Reiniciar temporizador si no hay rostro
            tiempo_ojos_cerrados_inicio = None

        # Mostrar estado en el frame
        cv2.putText(frame, text=texto_estado_display, org=(10, 30), fontFace=fuente,
                    fontScale=0.8, color=color_estado_display, thickness=2, lineType=cv2.LINE_AA)

        # Calcular y mostrar FPS
        capturaTiempoFrame = time.time()
        fps = 0
        if capturaTiempoFrame > anteriorTiempoFrame:
             fps = 1 / (capturaTiempoFrame - anteriorTiempoFrame)
        anteriorTiempoFrame = capturaTiempoFrame
        cv2.putText(frame, text=f'FPS: {int(fps)}', org=(frame.shape[1] - 120, 30), fontFace=fuente,
                    fontScale=0.8, color=(255, 255, 0), thickness=2, lineType=cv2.LINE_AA)

        cv2.imshow("Detector de Somnolencia (ESC para salir)", frame)

        tecla = cv2.waitKey(1) & 0xFF
        if tecla == ord('e'):
            rotacion = 1 if rotacion == 0 else 0
            print(f"Efecto espejo: {'Activado' if rotacion == 1 else 'Desactivado'}")
        elif tecla == ord('q'):
            verMalla = not verMalla
            print(f"Mostrar malla: {'Activado' if verMalla else 'Desactivado'}")
        elif tecla == 27:
            print("Tecla ESC presionada. Saliendo...")
            break

    # --- Fin del bucle ---
    if vectorEstado:
        print("Generando gráfico de estados...")
        analizarDatos(vectorEstado)
    else:
        print("No se generaron datos para el gráfico.")


def analizarDatos(vectorEstado):
    """
    Muestra un gráfico simple del estado de la alerta a lo largo del tiempo.
    """
    try:
        plt.figure(figsize=(10, 5))
        # Convertir 'abierto' a 0 y 'cerrado' (alerta activa) a 1
        estados_num = [1 if estado == "cerrado" else 0 for estado in vectorEstado]
        plt.plot(estados_num)
        plt.title('Análisis de Alerta de Somnolencia')
        plt.xlabel('Tiempo (frames)')
        plt.ylabel('Estado Alerta (1=Activa, 0=Inactiva)')
        plt.yticks([0, 1], ['Inactiva', 'Activa'])
        plt.grid(True)
        plt.ylim(-0.1, 1.1)
        plt.show()
    except Exception as e:
        print(f"No se pudo generar el gráfico: {e}")
        print("Asegúrate de tener matplotlib instalado: pip install matplotlib")

# --- Punto de entrada del script ---
if __name__ == "__main__":
    main()



# --------------------------------------------------------------------------------



#   CODIGO NUMERO 1 FUNCIONAL
'''
import cv2 # Opencv
import mediapipe as mp # Google
import time
import matplotlib.pyplot as plt # Para graficar (opcional al final)

# Importaciones de tus módulos
from Captura import Captura
from MallaFacial import MallaFacial
from AnalisisFacial import AnalisisFacial
from ArduinoComunicador import ArduinoComunicador # Nueva clase para Arduino

# --- Configuración ---
# URL de DroidCam (asegúrate que sea la correcta y accesible desde tu PC)
droidcam_url = "http://192.168.1.5:4747/video"

# Puerto serial de Arduino
puerto_arduino = "COM7"

# Fuente de texto para OpenCV
fuente = cv2.FONT_ITALIC

# --- Funciones ---

def main():
    """
    Función principal que inicializa los objetos y comienza el análisis.
    """
    # Inicializar la captura de video usando DroidCam
    objetoCaptura = Captura(fuente_video=droidcam_url)
    captura = objetoCaptura.getCaptura()

    # Verificar si la captura se inició correctamente
    if captura is None:
        print("No se pudo iniciar la captura de video. Saliendo.")
        return # Salir si no hay video

    # Inicializar la comunicación con Arduino
    arduino_com = ArduinoComunicador(puerto=puerto_arduino)
    arduino_com.conectar() # Intenta conectar

    # Inicializar la malla facial de MediaPipe
    objetoMallaFacial = MallaFacial()
    mediapMallaFacial, mallaFacial = objetoMallaFacial.getMallaFacial()
    mediapDibujoPuntos, dibujoPuntos = objetoMallaFacial.getPuntosMallaFacial()

    # Iniciar el análisis del video
    try:
        analisisVideo(captura, mediapDibujoPuntos, dibujoPuntos, mediapMallaFacial, mallaFacial, arduino_com)
    except Exception as e:
        print(f"Ocurrió un error durante la ejecución: {e}")
    finally:
        # Asegurarse de liberar recursos al finalizar o en caso de error
        print("Limpiando recursos...")
        objetoCaptura.liberar() # Libera la captura de video
        arduino_com.desconectar() # Cierra la conexión con Arduino
        cv2.destroyAllWindows() # Cierra todas las ventanas de OpenCV
        print("Recursos liberados. Saliendo.")


def analisisVideo(captura, mediapDibujoPuntos, dibujoPuntos, mediapMallaFacial, mallaFacial, arduino_com):
    """
    Procesa el video frame a frame, detecta somnolencia y envía señales a Arduino.
    """
    vectorEstado = [] # Para guardar estados (usado para graficar al final)
    verMalla = False # Flag para mostrar o no la malla facial
    rotacion = 1 # 1 para efecto espejo, 0 para normal

    anteriorTiempoFrame = 0
    capturaTiempoFrame = 0

    while True:
        # Lectura de frame y el estado
        estado, frame = captura.read()

        # Si no se pudo leer el frame (fin del video o error)
        if not estado:
            print("No se pudo leer el frame. Terminando bucle.")
            break

        # Aplicar efecto espejo si está activado
        if rotacion != 0:
            frame = cv2.flip(frame, rotacion)

        # Convertir frame a RGB (MediaPipe lo espera en RGB)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Procesar el fotograma para obtener la malla facial
        resultados = mallaFacial.process(frame_rgb)

        listaPuntosFaciales = []
        mensaje_somnolencia = "no" # Estado por defecto: alerta

        # Si se detecta al menos un rostro
        if resultados.multi_face_landmarks:
            # Iterar sobre cada rostro detectado (normalmente solo uno)
            for rostros in resultados.multi_face_landmarks:
                # Dibujar la malla facial si está activado
                if verMalla:
                    mediapDibujoPuntos.draw_landmarks(
                        image=frame, # Dibujar sobre el frame original BGR
                        landmark_list=rostros,
                        connections=mediapMallaFacial.FACEMESH_CONTOURS,
                        landmark_drawing_spec=dibujoPuntos,
                        connection_drawing_spec=dibujoPuntos)

                # Extraer las coordenadas de los puntos clave
                listaPuntosFaciales.clear() # Limpiar lista para este rostro
                for puntoID, puntos in enumerate(rostros.landmark):
                    altoVentana, anchoVentana, _ = frame.shape
                    posx = int(puntos.x * anchoVentana)
                    posy = int(puntos.y * altoVentana)
                    listaPuntosFaciales.append([puntoID, posx, posy])

                # Si tenemos todos los puntos (468 para MediaPipe Face Mesh)
                if len(listaPuntosFaciales) == 468:
                    # Analizar los puntos para detectar somnolencia
                    objetoAnalisisFacial = AnalisisFacial(listaPuntosFaciales)
                    mensaje_somnolencia = objetoAnalisisFacial.getLongitudes() # Devuelve 'yes' o 'no'

                    # Mostrar estado en el frame y enviar señal a Arduino
                    if mensaje_somnolencia == 'yes':
                        # Somnolencia detectada
                        cv2.putText(frame, text='SOMNOLENCIA DETECTADA!', org=(10, 30), fontFace=fuente,
                                    fontScale=0.8, color=(0, 0, 255), thickness=2, lineType=cv2.LINE_AA)
                        arduino_com.enviar_senal('1') # Enviar señal de alerta a Arduino
                    else:
                        # Conductor alerta
                        cv2.putText(frame, text='Conductor Alerta', org=(10, 30), fontFace=fuente,
                                    fontScale=0.8, color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)
                        arduino_com.enviar_senal('0') # Enviar señal de normalidad a Arduino

                    # Opcional: Mostrar ejes de rotación (si la función existe y es necesaria)
                    # mostrarEjesRotacion(listaPuntosFaciales, frame, altoVentana)

                    # Guardar estado para gráfico final
                    estado_grafico = "cerrado" if mensaje_somnolencia == "yes" else "abierto"
                    vectorEstado.append(estado_grafico)

        else:
            # No se detectó rostro, enviar señal de normalidad por precaución
            cv2.putText(frame, text='No se detecta rostro', org=(10, 60), fontFace=fuente,
                        fontScale=0.7, color=(0, 255, 255), thickness=2, lineType=cv2.LINE_AA)
            arduino_com.enviar_senal('0')


        # Calcular y mostrar FPS
        capturaTiempoFrame = time.time()
        fps = 0
        if capturaTiempoFrame > anteriorTiempoFrame:
             fps = 1 / (capturaTiempoFrame - anteriorTiempoFrame)
        anteriorTiempoFrame = capturaTiempoFrame
        cv2.putText(frame, text=f'FPS: {int(fps)}', org=(frame.shape[1] - 120, 30), fontFace=fuente,
                    fontScale=0.8, color=(255, 255, 0), thickness=2, lineType=cv2.LINE_AA)

        # Mostrar el frame procesado
        cv2.imshow("Detector de Somnolencia (ESC para salir)", frame)

        # Manejo de teclas
        tecla = cv2.waitKey(1) & 0xFF
        if tecla == ord('e'): # Cambiar efecto espejo
            rotacion = 1 if rotacion == 0 else 0
            print(f"Efecto espejo: {'Activado' if rotacion == 1 else 'Desactivado'}")
        elif tecla == ord('q'): # Activar/Desactivar malla
            verMalla = not verMalla
            print(f"Mostrar malla: {'Activado' if verMalla else 'Desactivado'}")
        elif tecla == 27: # Tecla ESC
            print("Tecla ESC presionada. Saliendo...")
            break # Salir del bucle while

    # --- Fin del bucle ---

    # Opcional: Analizar y mostrar gráfico después de cerrar la ventana
    if vectorEstado:
        print("Generando gráfico de estados...")
        analizarDatos(vectorEstado)
    else:
        print("No se generaron datos para el gráfico.")


def analizarDatos(vectorEstado):
    """
    Muestra un gráfico simple del estado de los ojos a lo largo del tiempo.
    """
    try:
        plt.figure(figsize=(10, 5)) # Tamaño de la figura
        # Convertir 'abierto' a 1 y 'cerrado' a 0 para graficar mejor
        estados_num = [1 if estado == "abierto" else 0 for estado in vectorEstado]
        plt.plot(estados_num)
        plt.title('Análisis del Estado de los Ojos')
        plt.xlabel('Tiempo (frames)')
        plt.ylabel('Estado (1=Abierto, 0=Cerrado)')
        plt.yticks([0, 1], ['Cerrado', 'Abierto']) # Etiquetas en el eje Y
        plt.grid(True) # Añadir rejilla
        plt.ylim(-0.1, 1.1) # Ajustar límites del eje Y
        plt.show()
    except Exception as e:
        print(f"No se pudo generar el gráfico: {e}")
        print("Asegúrate de tener matplotlib instalado: pip install matplotlib")

# --- Punto de entrada del script ---
if __name__ == "__main__":
    main()
'''