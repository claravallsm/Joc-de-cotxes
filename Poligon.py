from worldview.WPoint import *
import math
    # Representa una figura geomètrica de n vèrtexs en un espai bidimensional.
    # Proporciona mètodes per a la rotació, visualització, eliminació detecció de col·lisions i de si un punt 
    # donat esta contingut en el poligon.
class Poligon:
    # Per definir un polígon cal una llista de vèrtexs (en aquest cas Wpoint)
    def __init__(self, llista_punts):
        self.vertexs = llista_punts 
    
    # Gira el polígon al voltant del seu centre geomètric usant matrius de rotació.
    def rotar(self, angle_graus):
        angle_rad = math.radians(angle_graus)
        
        # Centre del polígon 
        cx = sum(p.x for p in self.vertexs) / len(self.vertexs)
        cy = sum(p.y for p in self.vertexs) / len(self.vertexs)
        
        nous_vertexs = []
        
        for p in self.vertexs:
            # Posició relativa al centre
            temp_x = p.x - cx
            temp_y = p.y - cy
            
            rx = temp_x * math.cos(angle_rad) - temp_y * math.sin(angle_rad)
            ry = temp_x * math.sin(angle_rad) + temp_y * math.cos(angle_rad)
                
            # Torno a coordenades mundials
            nous_vertexs.append(WPoint(rx + cx, ry + cy))     
        self.vertexs = nous_vertexs

    # Converteix els vèrtexs del polígon del món a píxels de pantalla i pinta la forma d'un color especificat.
    def pinta(self, canvas, wv, color_interior,color_exterior):
        punts_pantalla = []
        for p in self.vertexs:
            v = wv.worldToView(p) 
            punts_pantalla.extend([v.x, v.y]) 
        canvas.create_polygon(punts_pantalla, fill=color_interior, outline=color_exterior)
   
    # Elimina les dades de vèrtexs d'un poligon 
    def remove(self,llista_punts):
        llista_punts.clear()

    # Detecta la intersecció amb un altre polígon mitjançant el Separating Axis Theorem (SAT).
    # L'algorisme és altament eficient (O(n)) per a polígons convexos.
    # return: True si hi ha intersecció, False si no.
    def colisiona(self, altre):
            poligons = [self, altre]
            for poligon in poligons:
                for i in range(len(poligon.vertexs)):
                    p1 = poligon.vertexs[i]
                    p2 = poligon.vertexs[(i + 1) % len(poligon.vertexs)]
                    axis = (-(p2.y - p1.y), p2.x - p1.x) #vector normal
                    
                    min_pol, max_pol = self._projectar(axis)
                    min_pol2, max_pol2= altre._projectar(axis)
                    
                    # Si hi ha un espai buit, NO es toquen
                    if max_pol < (min_pol2-0.01) or max_pol2 < (min_pol-0.01):
                        return False
            return True 

    # Comprova si un punt és dins del polígon utilitzant l'algoritme de Ray Casting. Si el làser creua un nombre imparell de parets, 
    # el punt està a dins; si en creua un nombre parell, està a fora. S'utilitza una tolerància horitzontal per compensar micro-errors de precisió.
    # Retorna un boleà que indica la inclusió del punt.
    def conte_punt(self, punt, tolerancia=2):
        x, y = punt.x, punt.y
        dins = False
        n = len(self.vertexs)
        
        for i in range(n):
            p1 = self.vertexs[i]
            p2 = self.vertexs[(i + 1) % n]
            #cal una y més gran i l'altra més peque i que la valla quedi a la dreta (si no ja l'haurem passat)
            if ((p1.y > y) != (p2.y > y)) and  (x < (p2.x - p1.x) * (y - p1.y) / (p2.y - p1.y) + p1.x + tolerancia):
                dins = not dins # Cada vegada que detectem que el raig creua una paret, canviem l'estat.         
        return dins
    
    # Projecta tots els vèrtexs sobre un eix i retorna una tupla amb el valor mínim i màxim.
    def _projectar(self, axis):
        valors = []
        for p in self.vertexs:
            projeccio = p.x * axis[0] + p.y * axis[1] # Producte escalar sobre l'eix
            valors.append(projeccio)
        return min(valors), max(valors)