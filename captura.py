import cv2 #Opencv

class Captura:
    """
    Clase para manejar la captura de video desde diferentes fuentes.
    """
    captura=None
    fuente_video=None

    def __init__(self, fuente_video=0):
        """
        Inicializa la captura de video.

        Args:
            fuente_video (int or str): Índice de la cámara (e.g., 0 para webcam integrada)
                                       o URL del stream de video (e.g., DroidCam IP).
                                       Por defecto es 0.
        """
        self.fuente_video = fuente_video
        print(f"Inicializando captura desde: {self.fuente_video}")

    def getCaptura(self):
        """
        Intenta abrir la fuente de video especificada.

        Returns:
            cv2.VideoCapture or None: Objeto de captura si tiene éxito, None si falla.
        """
        try:
            # Intenta abrir la fuente de video (índice o URL)
            self.captura = cv2.VideoCapture(self.fuente_video)

            # Verifica si la captura se abrió correctamente
            if not self.captura.isOpened():
                print(f"Error: No se pudo abrir la fuente de video: {self.fuente_video}")
                self.captura = None
            else:
                print(f"Fuente de video abierta correctamente: {self.fuente_video}")

        except Exception as e:
            print(f"Excepción al abrir la fuente de video: {e}")
            self.captura = None

        return self.captura

    def liberar(self):
        """
        Libera el objeto de captura si está abierto.
        """
        if self.captura and self.captura.isOpened():
            self.captura.release()
            print("Captura de video liberada.")

