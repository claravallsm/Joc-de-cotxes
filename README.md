# Simulador de Cotxes: Conducció i Obstacles

Aquest projecte és una simulació interactiva de vehicles desenvolupada en **Python** utilitzant la llibreria gràfica **Tkinter**. El programa permet gestionar la física de moviment d'un vehicle, la detecció de col·lisions i la interacció amb un entorn dinàmic definit mitjançant fitxers de dades.

## Característiques Principals

* **Motor de Joc:** Gestió de moviment sobre una finestra.
* **Càmera Dinàmica:** Seguiment automàtic del vehicle principal (cotxe blanc) per mantenir-lo sempre centrat.
* **Gestió de Circuits:** Mapes carregats mitjançant fitxers **JSON**, permetent definir la geometria de la carretera.
* **Sistema de Col·lisions:** Detecció en temps real entre vehicles i obstacles.
* **Modes de Joc:**
    * **Conducció Normal:** Mode lliure per circular amb cotxes que van amb el mateix sentit.
    * **Mode Obstacles:** Mode de supervivència amb recollida d'objectes i trànsit en contra:
        * 🟨 **Blocs Grocs:** Atorguen vides extra. Pretenen simular "monedes".
        * 🟥 **Blocs Vermells:** Resten vides al jugador. Pretenen simular "obstacles".

## Controls

Utilitza el teclat per controlar el vehicle blanc:

| Tecla | Acció |
| :--- | :--- |
| **↑** | Accelerar |
| **↓** | Frenar  |
| **←** | Girar a l'esquerra |
| **→** | Girar a la dreta |

---

##  Instal·lació i Compilació

El projecte requereix una instal·lació estàndard de Python 3. Segueix aquests passos per executar-lo:

1.  **Clona o descarrega** els fitxers del repositori.
2.  Assegura't de tenir instal·lat **Python 3**.
3.  Obre una terminal al directori del projecte.
4.  Executa el fitxer principal amb la següent comanda:

```bash
python animacio.py
