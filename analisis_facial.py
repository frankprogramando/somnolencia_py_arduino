from ast import Return
import math

class AnalisisFacial:
     
    longitudes=None
    listaPuntosFaciales=None
    longitudOjoIzquierdo=None
    longitudOjoDerecho=None
 
    emocion=None

    def __init__(self,listaPuntosFaciales) :  
       self.listaPuntosFaciales=listaPuntosFaciales

    def getLongitudes(self):
        xpuntaRostro1,yPuntaRostro1=self.listaPuntosFaciales[93][1:]
        xpuntaRostro2,yPuntaRostro2=self.listaPuntosFaciales[323][1:]
        self.longitudRostro=math.hypot(xpuntaRostro1-xpuntaRostro2,yPuntaRostro1-yPuntaRostro2)
        #print(f"Longitud Rostro {longitudRostro}")
        #Trabajamos con proporciones 240 es el 100%
        porcentaje=self.longitudRostro/240
        #print(f"Porcentaje {int(porcentaje*100)}% Decimal {int(porcentaje*100)}")
        #print(f"Tamaño rostro proporcional {self.longitudRostro/porcentaje}")
        #Segun el identificador tomamos coordenadas en x,y ([n:] desde la posicion n en adelante)

        x1OjoIzquierdo,y1OjoIzquierdo=self.listaPuntosFaciales[159][1:]
        x2OjoIzquierdo,y2OjoIzquierdo=self.listaPuntosFaciales[145][1:]
        #Devuelve la norma de un vector es decir distancia entre dos puntos
        self.longitudOjoIzquierdo=abs(math.hypot(x2OjoIzquierdo-x1OjoIzquierdo,y2OjoIzquierdo-y1OjoIzquierdo)/porcentaje)
        #print(f"Longitud Ojo Izquierdo:{self.longitudOjoIzquierdo}")
        x1OjoDerecho,y1OjoDerecho=self.listaPuntosFaciales[374][1:]
        x2OjoDerecho,y2OjoDerecho=self.listaPuntosFaciales[386][1:]
        #Devuelve la norma de un vector es decir distancia entre dos puntos
        self.longitudOjoDerecho=abs(math.hypot(x2OjoDerecho-x1OjoDerecho,y2OjoDerecho-y1OjoDerecho)/porcentaje)
        #print(f"Longitud Ojo Derecho:{self.longitudOjoDerecho}")
        
        if self.longitudOjoIzquierdo<=12:
            escalaLongitudOjoIzquierdo="ojoI_cerrado" 
        elif  self.longitudOjoIzquierdo>10:  
             escalaLongitudOjoIzquierdo="ojoI_abierto"    

        if self.longitudOjoDerecho<=12:
            escalaLongitudOjoDerecho="ojoD_cerrado"  
        elif self.longitudOjoDerecho>10:  
             escalaLongitudOjoDerecho="ojoD_abierto"
      
        return self.analisisSueño(escalaLongitudOjoDerecho,escalaLongitudOjoIzquierdo)

    def analisisSueño(self,escalaLongitudOjoDerecho,escalaLongitudOjoIzquierdo):
        if (escalaLongitudOjoDerecho=="ojoD_cerrado"):
            return "yes"
        if (escalaLongitudOjoIzquierdo=="ojoI_cerrado"):
            return "yes"    
        return "no"