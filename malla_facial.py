import mediapipe as mp

class MallaFacial:

    mallaFacial=None
    puntosMallaFacial=None

    def __init__(self):    
        #Creamos un objeto donde almacenar la malla facial
        mediapMallaFacial=mp.solutions.face_mesh
        #Creamos el objeto de la malla facial
        mallaFacial=mediapMallaFacial.FaceMesh()
        self.mallaFacial=mediapMallaFacial,mallaFacial
        
        #Creamos un objeto donde almacenar los puntos faciales de mediapipe
        mediapDibujoPuntos=mp.solutions.drawing_utils
        #Asignamos valores a los puntos 
        #Color BGR
        puntosMalla=mediapDibujoPuntos.DrawingSpec(thickness=1,circle_radius=0,color=(255,255,0))
        self.puntosMallaFacial=mediapDibujoPuntos,puntosMalla

    def getMallaFacial(self):      
        return self.mallaFacial

    def getPuntosMallaFacial(self):
        return self.puntosMallaFacial       