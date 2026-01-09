import math
from worldview.WPoint import *
from Poligon import Poligon

# Representa un segment de carretera corbat que connecta dos trams rectangulars.
# Aquesta classe genera un polígon complex calculant dos arcs concèntrics  (interior i exterior) per definir la 
# superfície de la calçada.
# És un cas particular de poligon, a més hi ha una funció que crea la corba donats l'angle inicial, final i un radi.
class Corba(Poligon):
    def __init__(self, x, y, radi, angle_ini, angle_fi, ample=100, particions=20):
        self.x = x
        self.y = y
        self.radi = radi
        self.angle_ini=angle_ini
        self.angle_fi=angle_fi
        self.ample = ample
        self.particions= particions
        
        # Generem els punts de la carretera
        vertexs = self.CreaCorba(angle_ini, angle_fi, particions)
        
        # Cridem al pare Poligon amb la llista de punts
        super().__init__(vertexs)
    
    # Calcula els vèrtexs que defineixen el contorn de la corba. Genera dos arcs i els combina per formar un 
    # polígon tancat.  Retorna una lista de WPoints que defineixen el perímetre total.
    def CreaCorba(self, angle_ini, angle_fi, particions):
        punts_ext = []
        punts_int = []
        
        r_ext = self.radi + (self.ample / 2) # dona positiu
        r_int = self.radi - (self.ample / 2) # dona negatiu
        diff = angle_fi - angle_ini
        
        for i in range(particions + 1):
            # Calculem l'angle en cada pas
            angle_rad = math.radians(angle_ini + (diff * i / particions))
            
            # Vora exterior
            ex =  self.x+ r_ext * math.cos(angle_rad) 
            ey = self.y + r_ext * math.sin(angle_rad)
            punts_ext.append(WPoint(ex, ey))
            
            # Vora interior
            ix = self.x+ r_int * math.cos(angle_rad) 
            iy = self.y+ r_int * math.sin(angle_rad)
            punts_int.append(WPoint(ix, iy))
        punts_int.reverse()
        return punts_ext + punts_int

    # Converteix els vèrtexs de la corba del món a píxels de pantalla i pinta la corba de color gris.
    def pinta(self, canvas, wv):
        super().pinta(canvas, wv, "grey","grey")
    
    # Comprova si un punt és dins de la corba utilitzant l'algoritme de Ray Casting. Si el làser creua un nombre imparell de parets, 
    # el punt està a dins; si en creua un nombre parell, està a fora. S'utilitza una tolerància horitzontal per compensar micro-errors de precisió.
    # Retorna un boleà que indica la inclusió del punt.
    def conte_punt(self, punt):
        return super().conte_punt(punt)