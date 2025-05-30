import cv2

#   IMPLEMENTACIÓN DE UNA CAMARA DE SEGURIDAD

# Dirección RTSP de tu cámara
rtsp_url = "rtsp://admin:Elpekas123@192.168.1.14:554/live/ch0"  # Modificar con tus credenciales

# Abrir el flujo de video
cap = cv2.VideoCapture(rtsp_url)

# Verificar que la conexión fue exitosa
if not cap.isOpened():
    print("Error: No se pudo conectar al flujo RTSP.")
    exit()

# Capturar y procesar los frames
while True:
    ret, frame = cap.read()
    if not ret:
        print("Error al leer el flujo.")
        break
    
    # Aquí puedes aplicar la detección de somnolencia o cualquier procesamiento
    cv2.imshow("Flujo de Video", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):  # Salir con 'q'
        break

cap.release()
cv2.destroyAllWindows()
