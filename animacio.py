from tkinter import *
import time
import json
import math

from Poligon import *
from Cotxe import *
from Tram import *
from Corba import *
from worldview.VPoint import *
from worldview.WPoint import *
from worldview.WorldView import *

'''Aquest és el fitxer central del treball que fa que funcioni la simulació carregant la geometria dels trams i les dades dels cotxes des d'un fitxer JSON. 
Gestiona el menú inicial interactiu per permetre a l'usuari triar entre el mode de joc estàndard o amb obstacles.
Executa el bucle principal que captura les entrades del teclat per controlar la velocitat i el gir del vehicle en temps real.
Coordina la càmera dinàmica del WorldView perquè segueixi constantment la posició del jugador al llarg de tot el circuit.
Verifica constantment la física del joc, detectant col·lisions entre vehicles i comprovant si el cotxe es manté sobre l'asfalt.
Administra la interfície gràfica lateral, el sistema de vides per cors i les pantalles de victòria o Game Over.'''

#Aquesta funció llegeix el fitxer JSON proposat, retornant la llista de cotxes i trams.
#Retornem les 2 llistes per separat, ja que una funció de python pot retornar n valors, separats per coma.
def lectura_json(fitxer):
    f=open(fitxer,"r")
    dades=json.load(f)
    f.close()
    trams=[]
    for t in dades['sections']:
        t1=Tram(t['position']['x'],t['position']['y'],t['distance'],t['angle'])
        trams.append(t1)
    cotxes=[]
    for c in dades['cars']:
        index_tram = c['tram']
        angle_ini = trams[index_tram].angle
        c1=Cotxe(c['start_position']['x'],c['start_position']['y'],c['width'],c['height'],angle_ini,index_tram,c['sentit']) #la direccio no importa com p.ex dreta 0 graus i esquerra 180 graus
        c1.x_ini = c['start_position']['x']
        c1.y_ini = c['start_position']['y']
        c1.angle_ini = angle_ini
        c1.tram_ini=c['tram']
        cotxes.append(c1)
    return cotxes,trams 
# Gestió de l'estat inicial del joc
joc_iniciat = False
mode_obstacles = False
obstacles=[]
# Gestiona la selecció de mode de joc en el menú principal.
def detectar_clic(event):
    global joc_iniciat, mode_obstacles,obstacles
    if 300 <= event.x <= 700 and 250 <= event.y <= 320:
        mode_obstacles = False
        joc_iniciat = True 
    elif 300 <= event.x <= 700 and 350 <= event.y <= 420:
        mode_obstacles = True
        joc_iniciat = True
# Dibuixa el panell lateral de control i el resum de l'estat (vides).
def dibuixa_interficie(canvas, vides):
    # Fons del panell lateral
    canvas.create_rectangle(800, 0, 1000, 600, fill="white", outline="")
    canvas.create_rectangle(800, 0, 1005, 605, fill="#1a1a1a", outline="#FF9F00", width=3)
    
    # Secció de Controls
    canvas.create_text(900, 45, text="CONTROLS", fill="#FF9F00", font=("Arial", 14, "bold"))
    canvas.create_line(820, 65, 980, 65, fill="#444444")
    controls = [("↑", "ACCELERA"), ("↓", "FRENA"), ("←", "ESQUERRA"), ("→", "DRETA")]
    y = 100
    for icona, accio in controls:
        canvas.create_text(830, y, text=icona, fill="#FF9F00", font=("Arial", 18, "bold"), anchor="w")
        canvas.create_text(870, y, text=accio, fill="white", font=("Verdana", 9, "bold"), anchor="w")
        y += 45
    canvas.create_text(830, 280, text="■: +1 Vida", fill="yellow", font=("Verdana", 9, "bold"), anchor="w")
    canvas.create_text(830, 325, text="■: -1 Vida", fill="red", font=("Verdana", 9, "bold"), anchor="w")

    # Resum de vides
    canvas.create_text(900, 400 , text="RESUM", fill="#FF9F00", font=("Arial", 14, "bold"))
    canvas.create_line(820, 420, 980, 420, fill="#444444")
    canvas.create_text(865, 435, text="VIDES", fill="white", font=("Verdana", 12, "bold"), anchor="w")
    
    # Dibuixem els cors en files de 4 per a que no surtin de la pantalla
    x_base = 880
    y_base = 460
    for i in range(vides):
        fila = i // 4  # divisió sencera
        columna = i % 4
        canvas.create_text(x_base + (columna * 25), y_base + (fila * 20), 
                           text="❤️", font=("Arial", 12), fill="red")

    # Pantalla de Final de Joc
    if vides == 0:
        canvas.create_rectangle(0, 0, 1000, 600, fill="black", stipple="gray75")
        canvas.create_text(500, 300, text="GAME OVER", fill="red", font=("Impact", 60, "bold"))
        canvas.update()
        time.sleep(3) 

# Genera un quadrat (polígon) que actua com a moneda/obstacle.
def crear_moneda(x, y,mida=5):
        return Poligon([
            WPoint(x - mida, y - mida), 
            WPoint(x + mida, y - mida), 
            WPoint(x + mida, y + mida), 
            WPoint(x - mida, y + mida)
        ])

# Dibuixa la línia de meta amb el patró de quadres clàssic al final de l'últim tram.
def dibuixa_meta(canvas, wv, ultim_tram):
    p = ultim_tram.p_final
    mida_quadre = 5
    num_quadres_ample = 20  
    num_quadres_fons = 2    
    
    # Càlcul de la meitat de l'amplada total (per centrar)
    offset_x = (num_quadres_ample * mida_quadre) / 2 
    offset_y = (num_quadres_fons * mida_quadre) / 2  

    for i in range(num_quadres_ample):
        for j in range(num_quadres_fons):
            color = "white" if (i + j) % 2 == 0 else "black"
            # Coordenades: restem l'offset per centrar-ho en p.x i p.y
            qx = p.x + (i * mida_quadre) - offset_x
            qy = p.y + (j * mida_quadre) - offset_y
            
            q_pol = Poligon([
                WPoint(qx, qy),
                WPoint(qx + mida_quadre, qy),
                WPoint(qx + mida_quadre, qy + mida_quadre),
                WPoint(qx, qy + mida_quadre)
            ])
            q_pol.pinta(canvas, wv, color, color)

# Inicialització de la finestra i del menú
tk=Tk()
w=Canvas(tk,width=1000,height=600)
w.pack()
w.bind("<Button-1>", detectar_clic)

# Menú Inicial (mentre no es tria cap opció de joc es mostra això)
while not joc_iniciat:
    w.create_rectangle(0, 0, 1000, 600, fill="#1a1a1a")
    w.create_text(500, 150, text="CARRERES DE COTXES", fill="#FF9F00", font=("Arial", 35, "bold"))
    
    w.create_rectangle(300, 250, 700, 320, fill="#333333", outline="#FF9F00", width=3)
    w.create_text(500, 285, text="JUGAR SENSE OBSTACLES", fill="white", font=("Arial", 12, "bold"))
    
    w.create_rectangle(300, 350, 700, 420, fill="#333333", outline="#FF9F00", width=3)
    w.create_text(500, 385, text="JUGAR AMB OBSTACLES", fill="white", font=("Arial", 12, "bold"))
    
    w.create_text(500, 500, text="Fes clic en una opció per començar", fill="#666666", font=("Arial", 10, "italic"))
    w.update()      
    time.sleep(0.01)  

# Configuració de la càmera (WorldView) que seguirà el moviment del cotxe que controla l'humà
wv = WorldView( WPoint(0-300,500-300),  WPoint(0+300,500+300),  VPoint(0, 0), VPoint(800, 600)) 
# wv = WorldView( WPoint(-1000,0),  WPoint(2000,3000),  VPoint(0, 0), VPoint(800, 600)) per si al lector li interessa veure un planol més gèneric

cotxes,trams=lectura_json("carretera.json")
corbes = []

# Generació automàtica de corbes per connectar els trams rectes
for i in range(len(trams) -1 ):
    t_actual = trams[i]     # El tram on som ara
    t_seguent = trams[(i+1) ]  # El tram que ve després

    # El centre de la corba serà el punt on es troben els dos trams
    centre_x = t_actual.p_final.x
    centre_y = t_actual.p_final.y
    
    # L'angle inicial de la corba és l'angle del primer tram
    # L'angle final de la corba és l'angle del segon tram
    angle_inici = t_actual.angle
    angle_fi = t_seguent.angle
    
    # Ara creem la corba que connecta els dos
    nova_corba = Corba(centre_x, centre_y, 2, angle_inici - 90, angle_fi - 90) 
    #restem 90 si passem de tram de 0 graus realment hem d mira de -90 a x
    corbes.append(nova_corba)
# Corba final per tancar el circuit 
nova = Corba(0, 500, 2, 0, 90) 
corbes.append(nova) 
vides=3

if(mode_obstacles==False):
    # borrem els cotxes que van del revés ja que estem a l'opció sense obstacles
    for i in range(len(cotxes) - 1, -1, -1):
        c = cotxes[i]
        if c.sentit < 0:
            c.remove(c.vertexs)
            cotxes.pop(i)
    while True and vides>0:
        w.delete("all") #esborrem la finestra
        cotxes[0].controlar()
        # pintem tots els trams i corbes
        for t in trams:
            t.pinta(w,wv)
        for c in corbes:
            c.pinta(w, wv)
        dibuixa_meta(w, wv, trams[-1])
        for i,c in enumerate(cotxes):
            x_abans = c.x
            y_abans = c.y
            if(c.mou(trams)==-1): # un cotxe arriba a meta
                if i==0: # si es el que controla l'humà imprimim que ha arribat
                    w.create_rectangle(0, 0, 1000, 600, fill="black", stipple="gray75")
                    w.create_text(500, 300, text="HAS ARRIBAT A META!", fill="gold", font=("Impact", 60, "bold"))
                    w.update()
                    time.sleep(3)
                    vides=-1 # volem que no sigue >0 i =0 tampoc que sino me surtirà game over
                    break
            if i==0:
                movx=cotxes[i].x -x_abans
                movy=cotxes[i].y -y_abans
                wv.translateWindow(movx,movy) #fem que la finestra segueixi al cotxe q controlem natros
            esta_totalment_dins = True
            for p in c.vertexs:
                punt_a_l_asfalt = False
                for t in (trams + corbes):
                    if t.conte_punt(p): 
                        punt_a_l_asfalt = True
                        break 
                if not punt_a_l_asfalt:
                    esta_totalment_dins = False
                    break 
            if not esta_totalment_dins:
                old_x, old_y = c.x, c.y
                c.reubicar(c.x_ini, c.y_ini, c.angle_ini, c.tram_ini) 
                if i == 0:
                    vides -= 1
                    wv.translateWindow(c.x - old_x, c.y - old_y) 

            for c1 in cotxes:
                if c1 != c and c.colisiona(c1):
                        if i == 0: 
                            vides -= 1
                            wv.translateWindow(c.x_ini - c.x, c.y_ini - c.y)
                        c.reubicar(c.x_ini, c.y_ini, c.angle_ini,c.tram_ini)
                        c1.reubicar(c1.x_ini, c1.y_ini, c1.angle_ini,c1.tram_ini)
                        break 
        
            if i == 0:
                color_cotxe = "white"
            else:
                color_cotxe = "green"
            c.pinta(w, wv,color_cotxe)
        dibuixa_interficie(w,vides)
        w.update() 
        time.sleep(5/1000) #50ms de pausa

if (mode_obstacles==True):
    recompenses_bones=[]
    recompenses_dolentes=[]
    for i, t in enumerate(trams):
        p1 = t.p_inici
        p2 = t.p_final
        # Calculem el vector que va d'inici a final
        dx = p2.x - p1.x
        dy = p2.y - p1.y

        # Punt 1 (al 20% del tram)
        m1_x = p1.x + 0.2 * dx
        m1_y = p1.y + 0.2 * dy

        # Punt 2 (al 40% del tram)
        m2_x = p1.x + 0.4 * dx
        m2_y = p1.y + 0.4 * dy

        # Punt 3 (al 60% del tram)
        m3_x = p1.x + 0.6 * dx
        m3_y = p1.y + 0.6 * dy

        # Punt 4 (al 80% del tram)
        m4_x = p1.x + 0.8 * dx
        m4_y = p1.y + 0.8 * dy
                
        if i % 2 == 0:
            recompenses_bones.append(crear_moneda(m1_x, m1_y))
            recompenses_dolentes.append(crear_moneda(m2_x, m2_y))
            recompenses_bones.append(crear_moneda(m3_x, m3_y))
            recompenses_dolentes.append(crear_moneda(m4_x, m4_y))
        else:
            recompenses_dolentes.append(crear_moneda(m1_x, m1_y))
            recompenses_bones.append(crear_moneda(m2_x, m2_y))
            recompenses_dolentes.append(crear_moneda(m3_x, m3_y))
            recompenses_bones.append(crear_moneda(m4_x, m4_y))
    while True and vides>0:
        w.delete("all") 
        cotxes[0].controlar()
        for t in trams:
            t.pinta(w,wv)
        for c in corbes:
            c.pinta(w, wv)
        dibuixa_meta(w, wv, trams[-1])
        for i,c in enumerate(cotxes):
            x_abans = c.x
            y_abans = c.y
            if(c.mou(trams)==-1): 
                if i==0:
                    w.create_rectangle(0, 0, 1000, 600, fill="black", stipple="gray75")
                    w.create_text(500, 300, text="HAS ARRIBAT A META!", fill="gold", font=("Impact", 60, "bold"))
                    w.update()
                    time.sleep(3)
                    vides=-1
                    break
            if i==0:
                movx=cotxes[i].x -x_abans
                movy=cotxes[i].y -y_abans
                wv.translateWindow(movx,movy) #fem que segueixi al cotxe que controlem natros
            esta_totalment_dins = True
            for p in c.vertexs:
                punt_a_l_asfalt = False
                for t in (trams + corbes):
                    if t.conte_punt(p): 
                        punt_a_l_asfalt = True
                        break 
                if not punt_a_l_asfalt:
                    esta_totalment_dins = False
                    break 
            if not esta_totalment_dins:
                old_x, old_y = c.x, c.y
                if c.sentit>0:
                    c.reubicar(c.x_ini, c.y_ini, c.angle_ini, c.tram_ini) 
                else:
                    c.reubicar(c.x_ini, c.y_ini, c.angle_ini+180, c.tram_ini) 
                if i == 0:
                    vides -= 1
                    wv.translateWindow(c.x - old_x, c.y - old_y) 

            # Comprovem si aquest cotxe xoca amb algun altre de la llista
            for c1 in cotxes:
                if c1 != c and c.colisiona(c1):
                        if i == 0: 
                            vides -= 1
                            wv.translateWindow(c.x_ini - c.x, c.y_ini - c.y)
                        if c.sentit>0:
                            c.reubicar(c.x_ini, c.y_ini, c.angle_ini,c.tram_ini)
                        else:
                            c.reubicar(c.x_ini, c.y_ini, c.angle_ini+180,c.tram_ini)
                        if c1.sentit>0:
                            c1.reubicar(c1.x_ini, c1.y_ini, c1.angle_ini,c1.tram_ini)
                        else:
                            c1.reubicar(c.x_ini, c.y_ini, c.angle_ini+180,c.tram_ini)
                        break 
                
            if i == 0:
                color_cotxe = "white"
            elif c.sentit > 0:
                color_cotxe = "green"
            else:
                color_cotxe ="yellow" 
            c.pinta(w, wv,color_cotxe)
            for r in recompenses_bones[:]: # Recorrem una còpia amb [:]
                r.pinta(w, wv, "yellow", "gold") # Canviem el color perquè es distingeixi
                if c.colisiona(r):
                    recompenses_bones.remove(r) # Borrem 
                    if i==0: vides += 1
                    break # sino poder volem borra a un element que hem borrat ia

            for r in recompenses_dolentes[:]:
                r.pinta(w, wv, "red", "darkred") # Color d'alerta
                if c.colisiona(r):
                    recompenses_dolentes.remove(r) 
                    if i==0: vides -= 1
                    break # sino poder volem borra a un element que hem borrat ia
        dibuixa_interficie(w,vides)
        w.update()
        time.sleep(50/1000) # 50 ms de pausa