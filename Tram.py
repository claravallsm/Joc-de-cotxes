from worldview.WPoint import *
from worldview.LinearEquation import *
from Poligon import Poligon
import math
# Representa un segment de carretera rectangular definit per un punt inicial, una distància i un angle d'orientació.
# És un cas particular de poligon.
class Tram(Poligon):
    def __init__(self, x, y, distancia, angle):
        # Definim el punt d'inici (centre) 
        # . -----.
        # ! -----! les exclamacions son p._inici i p._final
        # .------.
        self.p_inici = WPoint(x, y)
        self.distancia = distancia
        self.angle = angle
        angle_radians=math.radians(angle)

        # Calculem el punt final usant l'angle i la distància
        self.p_final = WPoint(x + math.cos(angle_radians) * distancia, y + math.sin(angle_radians)* distancia)
        
        # Creem l'equació usant self.p_inici i  self.p_final (no l'usaré en el treball es deixa per futures millores)
        self.equacio = LinearEquation(self.p_inici, self.p_final)

        w=50 # Paràmetre de l'amplada de la via
        # Càclul del vector perpendicular a la direcció de la carretera
        dx = - w* math.sin(angle_radians)
        dy = w* math.cos(angle_radians)
        
        # Definició dels 4 vèrtexs del polígon que conformen la superfície de la carretera.
        # Es calcula aplicant el vector normal (+/- dx, dy) als punts inicial i final.
        vertexs = [ 
            WPoint(self.p_inici.x + dx , self.p_inici.y + dy ), 
            WPoint(self.p_final.x + dx, self.p_final.y + dy), 
            WPoint(self.p_final.x - dx, self.p_final.y - dy), 
            WPoint(self.p_inici.x - dx, self.p_inici.y - dy) 
        ]
        
        # Cridem al constructor del pare (Poligon) amb els vèrtexs calculats
        super().__init__(vertexs)

     # Converteix els vèrtexs del tram del món a píxels de pantalla i pinta el tram de color gris.
    def pinta(self,canvas,wv):
        super().pinta(canvas, wv, "grey","grey")
    
    # Gira el tram al voltant del seu centre geomètric usant matrius de rotació.
    def rotar(self,angle_graus):
        super().rotar(angle_graus)
    
    # Comprova si un punt és dins del tram utilitzant l'algoritme de Ray Casting. Si el làser creua un nombre imparell de parets, 
    # el punt està a dins del tram; si en creua un nombre parell, està a fora. S'utilitza una tolerància horitzontal per compensar micro-errors de
    # precisió.Retorna un boleà que indica la inclusió del punt.
    def conte_punt(self, punt,tolerancia=2):
        return super().conte_punt(punt,tolerancia)