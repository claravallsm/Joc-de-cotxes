import math
from worldview.WPoint import *
from Poligon import Poligon
import keyboard
# Representa un cotxe dins del simulador. És un cas particular de poligon.
# A més, implementa moviment segons els trams, també permet control per part de l'usuari i també permet reubicar el cotxe.
class Cotxe(Poligon):
    def __init__(self,x,y,w,h,angle,tram,sentit,v=1):
        self.x=x
        self.y=y
        self.w=w
        self.h=h
        self.v=v
        self.tram = tram
        self.sentit=sentit # sentit positiu: vol dir que es mou en la direcció del tram, negatiu: del revés
        # Notem que l'angle del cotxe vindrà donat per l'angle del tram doncs si volem que el cotxe
        # vagi del revés hem de sumar 180 graus a l'angle
        if self.sentit < 0:
            self.angle = (angle + 180) % 360
        else:
            self.angle = angle % 360
        # Creem els 4 vèrtexs relatius al centre
        hw, hh = w/2, h/2
        punts = [
            WPoint(x - hw, y - hh), 
            WPoint(x + hw, y - hh), 
            WPoint(x + hw, y + hh), 
            WPoint(x - hw, y + hh)
        ]
        #  0    1         
        #  3    2
        # Inicialitzem el polígon pare amb aquests punts
        super().__init__(punts)  
        self.sense_canvi_anglerotar(self.angle) # Rotació inicial
    
    # Calcula el desplaçament vectorial del vehicle. El vehicle es mou segons l'angle del tram.
    def mou(self, trams):
        v_restant = self.v 
        n_trams = len(trams)
        if self.sentit > 0:
            while v_restant > 0:
                tram_actual = trams[self.tram % n_trams]
                dist_feta = math.sqrt((self.x - tram_actual.p_inici.x)**2 + (self.y - tram_actual.p_inici.y)**2)
                dist_per_acabar = tram_actual.distancia - dist_feta

                if v_restant >= dist_per_acabar:
                    # Situem el cotxe al final del tram
                    dx, dy = tram_actual.p_final.x - self.x, tram_actual.p_final.y - self.y
                    self.x, self.y = tram_actual.p_final.x, tram_actual.p_final.y
                    for p in self.vertexs: p.x += dx; p.y += dy
                    v_restant -= dist_per_acabar 
                    # Canvi de tram
                    self.tram = (self.tram + 1) % n_trams 
                    # Si estic a l'últim tram i detecto que he de canviar vol dir que estic a meta!
                    if (self.tram==0): return -1 
                    nou_tram = trams[self.tram]
                    self.rotar(nou_tram.angle - self.angle) # Ajust relatiu
                else:
                    # Me moc pel tram segons l'angle
                    rad = math.radians(self.angle)
                    dx, dy = v_restant * math.cos(rad), v_restant * math.sin(rad)
                    self.x += dx; self.y += dy
                    for p in self.vertexs: p.x += dx; p.y += dy
                    v_restant = 0
        else:
            while v_restant > 0:
                tram_actual = trams[self.tram]
                # Distància que queda és la que hi ha fins a l'inici del tram (perquè anem cap enrere)
                dist_per_acabar = math.sqrt((self.x - tram_actual.p_inici.x)**2 + (self.y - tram_actual.p_inici.y)**2)
                if (v_restant +30 >= (dist_per_acabar)): # el + 30 arbitrari sinó no m'anava be
                    # Saltem a l'inici del tram 
                    dx, dy = tram_actual.p_inici.x - self.x, tram_actual.p_inici.y - self.y
                    self.x, self.y = tram_actual.p_inici.x, tram_actual.p_inici.y
                    for p in self.vertexs: p.x += dx; p.y += dy
                    v_restant -= dist_per_acabar
                    # Canvi de tram
                    if self.tram==0: self.tram=n_trams-1
                    else: self.tram = (self.tram - 1) % n_trams 
                    
                    nou_tram = trams[self.tram]
                    # Angle del tram + 180 per mirar en sentit contrari
                    angle_objectiu = (nou_tram.angle + 180) % 360
                    self.rotar(angle_objectiu - self.angle)
                else:
                    # Moviment normal (l'angle ja és correcte)
                    rad = math.radians(self.angle)
                    dx, dy = v_restant * math.cos(rad), v_restant * math.sin(rad)
                    self.x += dx; self.y += dy
                    for p in self.vertexs: p.x += dx; p.y += dy
                    v_restant = 0

     # Aquesta funció converteix les coordenades del món a píxels de pantalla i pinta la forma de color negre.
     # Inclou el dibuix d'un detall estètic (línia) per indicar en quin sentit es mou el cotxe.
    def pinta(self, canvas, wv, color):
        super().pinta(canvas, wv,color,"black")

        # Calculem el punt al 75% del costat esquerre (entre vèrtex 0 i 1)
        vec_esq_x = self.vertexs[1].x - self.vertexs[0].x
        vec_esq_y = self.vertexs[1].y - self.vertexs[0].y
        # Punt al 75% del camí
        p75_esq_x = self.vertexs[0].x + 0.75 * vec_esq_x
        p75_esq_y = self.vertexs[0].y + 0.75 * vec_esq_y
        p_esq_world = WPoint(p75_esq_x, p75_esq_y)

        # Calculem el punt al 75% del costat dret (entre vèrtex 3 i 2)
        vec_dret_x = self.vertexs[2].x - self.vertexs[3].x
        vec_dret_y = self.vertexs[2].y - self.vertexs[3].y
        # Punt al 75% del camí
        p75_dret_x = self.vertexs[3].x + 0.75 * vec_dret_x
        p75_dret_y = self.vertexs[3].y + 0.75 * vec_dret_y
        p_dret_world = WPoint(p75_dret_x, p75_dret_y)

        p1_screen = wv.worldToView(p_esq_world)
        p2_screen = wv.worldToView(p_dret_world)
        canvas.create_line(p1_screen.x, p1_screen.y, p2_screen.x, p2_screen.y, fill="black", width=2)
    
    # Aquesta funció canvia el centre i l'angle d'un cotxe
    def reubicar(self, nou_x, nou_y, nou_angle,nou_tram):
        self.x = nou_x
        self.y = nou_y
        self.tram = nou_tram
        self.angle = nou_angle
        
        #  Calculem els 4 vèrtexs bàsics 
        hw, hh = self.w/2, self.h/2
        self.vertexs = [
            WPoint( - hw,  - hh), 
            WPoint( + hw, - hh), 
            WPoint( + hw,  + hh), 
            WPoint( - hw,  + hh)
        ]
        # Apliquem la rotació inicial que li pertoca
        self.establir_angle(self.angle)
        for v in self.vertexs:
            v.x += self.x
            v.y += self.y
     
    #  Realitza una rotació incremental del vehicle.
    def rotar(self,angle_graus):
        self.angle+=angle_graus % 360
        super().rotar(angle_graus)
    
    #  Realitza una rotació incremental del vehicle sense canviar l'angle del vehicle.
    def sense_canvi_anglerotar(self,angle_graus):
        super().rotar(angle_graus)

    # Defineix un angle d'orientació absolut.
    def establir_angle(self,angle_graus):
        self.angle=angle_graus % 360
        super().rotar(angle_graus)
    
    # Gestiona les entrades de teclat en temps real per modificar la velocitat i l'angle.
    def controlar(self):
        if keyboard.is_pressed("down arrow"):
            self.v -= 0.1
        if keyboard.is_pressed("up arrow"):
            self.v += 0.1
        if keyboard.is_pressed("right arrow"):
            self.rotar(-0.5)
        if keyboard.is_pressed("left arrow"):
            self.rotar(0.5)
     
     # Elimina les dades de vèrtexs d'un cotxe 
    def remove(self,llista_punts):
        super().remove(llista_punts)  