import serial # Para comunicación serial
import time   # Para pausas

class ArduinoComunicador:
    """
    Clase para manejar la comunicación serial con Arduino.
    """
    arduino = None
    puerto = None
    baud_rate = 9600 # Tasa de baudios estándar
    conectado = False

    def __init__(self, puerto='COM7', baud_rate=9600, tiempo_espera=2):
        """
        Inicializa el comunicador Arduino.

        Args:
            puerto (str): Puerto serial al que está conectado Arduino (e.g., 'COM7').
            baud_rate (int): Tasa de baudios para la comunicación (debe coincidir con Arduino).
            tiempo_espera (int): Segundos para esperar a que se establezca la conexión.
        """
        self.puerto = puerto
        self.baud_rate = baud_rate
        self.tiempo_espera = tiempo_espera

    def conectar(self):
        """
        Intenta establecer la conexión serial con Arduino.
        """
        if self.conectado:
            print("Ya existe una conexión con Arduino.")
            return True

        try:
            print(f"Intentando conectar a Arduino en {self.puerto} a {self.baud_rate} baudios...")
            self.arduino = serial.Serial(self.puerto, self.baud_rate, timeout=1)
            time.sleep(self.tiempo_espera) # Espera a que la conexión serial se establezca
            self.conectado = True
            print("Conexión con Arduino establecida.")
            return True
        except serial.SerialException as e:
            print(f"Error al conectar con Arduino en {self.puerto}: {e}")
            print("El programa continuará sin comunicación con Arduino.")
            self.arduino = None
            self.conectado = False
            return False
        except Exception as e:
            print(f"Error inesperado al conectar con Arduino: {e}")
            self.arduino = None
            self.conectado = False
            return False

    def enviar_senal(self, senal):
        """
        Envía una señal (byte) a Arduino si está conectado.

        Args:
            senal (str): La señal a enviar ('1' para alerta, '0' para normalidad).
        """
        if not self.conectado or not self.arduino or not self.arduino.is_open:
            # print("Advertencia: No hay conexión con Arduino para enviar señal.")
            return # No hacer nada si no está conectado

        try:
            if senal == '1':
                self.arduino.write(b'1') # Enviar byte '1'
                # print("Señal '1' enviada a Arduino.")
            elif senal == '0':
                self.arduino.write(b'0') # Enviar byte '0'
                # print("Señal '0' enviada a Arduino.")
            else:
                print(f"Advertencia: Señal desconocida '{senal}'. No se envió nada.")
        except serial.SerialException as e:
            print(f"Error al escribir en Arduino: {e}")
            # Podríamos intentar reconectar o marcar como desconectado aquí
            self.conectado = False
            self.arduino.close()
            self.arduino = None
        except Exception as e:
            print(f"Error inesperado al enviar señal a Arduino: {e}")
            self.conectado = False
            if self.arduino and self.arduino.is_open:
                self.arduino.close()
            self.arduino = None


    def desconectar(self):
        """
        Cierra la conexión serial si está abierta.
        """
        if self.conectado and self.arduino and self.arduino.is_open:
            try:
                # Opcional: Enviar una señal de 'apagado' antes de cerrar
                self.enviar_senal('0')
                time.sleep(0.1) # Pequeña pausa
                self.arduino.close()
                self.conectado = False
                print("Conexión con Arduino cerrada.")
            except serial.SerialException as e:
                print(f"Error al cerrar la conexión con Arduino: {e}")
            except Exception as e:
                 print(f"Error inesperado al cerrar Arduino: {e}")
        elif self.conectado:
             # Si estaba marcado como conectado pero el objeto serial no existe o está cerrado
             self.conectado = False
             print("Conexión con Arduino ya estaba cerrada o era inválida.")
        # else:
        #      print("No había conexión activa con Arduino para cerrar.")





