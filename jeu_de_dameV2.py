# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 19:15:51 2026

@author: PC
"""

import os
import tkinter as tk
from tkinter import messagebox
import pygame

TAILLE_PLATEAU = 8
NB_AIDES_PAR_JOUEUR = 3
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class GestionnaireAudio:
    def __init__(self):
        self.son_clic = None
        self.son_capture = None
        self.initialise()

    def initialise(self):
        try:
            pygame.mixer.init()
        except Exception as e:
            print("Impossible d'initialiser le son :", e)
            return

        try:
            musique = os.path.join(BASE_DIR, 'musique.wav')
            if os.path.exists(musique):
                pygame.mixer.music.load(musique)
                pygame.mixer.music.play(-1)
        except Exception:
            pass

        self.son_clic = self.charger_son('clic.wav')
        self.son_capture = self.charger_son('capture.wav')

    def charger_son(self, nom):
        chemin = os.path.join(BASE_DIR, nom)
        if not os.path.exists(chemin):
            print("Son introuvable :", chemin)
            return None
        try:
            return pygame.mixer.Sound(chemin)
        except Exception as e:
            print("Impossible de charger", nom, ":", e)
            return None

    def jouer_clic(self):
        if self.son_clic:
            self.son_clic.play()

    def jouer_capture(self):
        if self.son_capture:
            self.son_capture.play()

    def arreter_musique(self):
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass


audio = GestionnaireAudio()
son_clic = audio.son_clic
son_capture = audio.son_capture

class Piece:
    def __init__(self, ligne, col, couleur):
        self.ligne = ligne
        self.col = col
        self.couleur = couleur
        self.dame = False
    def rendre_dame(self):
        self.dame = True

class JeuDeDames:
    def __init__(self):
        self.plateau = [[None for _ in range(TAILLE_PLATEAU)] for _ in range(TAILLE_PLATEAU)]
        self.joueur = 'white'
        self.pieces_capturees = {'white': [], 'black': []}
        self.aides_restantes = {'white': NB_AIDES_PAR_JOUEUR, 'black': NB_AIDES_PAR_JOUEUR}
        self.partie_terminee = False
        self.init_plateau()

    def init_plateau(self):
        for ligne in range(TAILLE_PLATEAU):
            for col in range(TAILLE_PLATEAU):
                if (ligne + col) % 2 == 1:
                    if ligne < 3:
                        self.plateau[ligne][col] = Piece(ligne, col, 'black')
                    elif ligne > 4:
                        self.plateau[ligne][col] = Piece(ligne, col, 'white')

    def obtenir_directions(self, piece):
        if piece.dame:
            return [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        sens = -1 if piece.couleur == 'white' else 1
        return [(sens, -1), (sens, 1)]

    def obtenir_coups_capture(self, piece):
        captures = []
        for dx, dy in self.obtenir_directions(piece):
            x1, y1 = piece.ligne + dx, piece.col + dy
            x2, y2 = piece.ligne + 2 * dx, piece.col + 2 * dy
            if 0 <= x1 < TAILLE_PLATEAU and 0 <= y1 < TAILLE_PLATEAU and 0 <= x2 < TAILLE_PLATEAU and 0 <= y2 < TAILLE_PLATEAU:
                cible = self.plateau[x1][y1]
                if cible and cible.couleur != piece.couleur and self.plateau[x2][y2] is None:
                    captures.append((x2, y2))
        return captures

    def deplacer(self, piece, ligne, col):
        if self.partie_terminee:
            return False
        if self.plateau[ligne][col] is not None:
            return False

        dx = ligne - piece.ligne
        dy = col - piece.col
        captures_possibles = self.obtenir_coups_capture(piece)

        if captures_possibles and (ligne, col) not in captures_possibles:
            return False

        if abs(dx) == 1 and abs(dy) == 1:
            if captures_possibles:
                return False
            if not piece.dame:
                sens = -1 if piece.couleur == 'white' else 1
                if dx != sens:
                    return False
            self.plateau[piece.ligne][piece.col] = None
            piece.ligne, piece.col = ligne, col
            self.plateau[ligne][col] = piece
            self.verifier_et_rendre_dame(piece)
            if son_clic:
                son_clic.play()
            return True

        elif abs(dx) == 2 and abs(dy) == 2:
            mil_x = (piece.ligne + ligne) // 2
            mil_y = (piece.col + col) // 2
            cible = self.plateau[mil_x][mil_y]
            if cible and cible.couleur != piece.couleur:
                self.plateau[piece.ligne][piece.col] = None
                self.plateau[mil_x][mil_y] = None
                self.pieces_capturees[cible.couleur].append(cible)
                piece.ligne, piece.col = ligne, col
                self.plateau[ligne][col] = piece
                self.verifier_et_rendre_dame(piece)
                if son_capture:
                    son_capture.play()
                return True
        return False

    def verifier_et_rendre_dame(self, piece):
        if piece.couleur == 'white' and piece.ligne == 0:
            piece.rendre_dame()
        elif piece.couleur == 'black' and piece.ligne == TAILLE_PLATEAU - 1:
            piece.rendre_dame()

    def obtenir_deplacements_valides(self, piece):
        captures = self.obtenir_coups_capture(piece)
        if captures:
            return captures

        deplacements = []
        for dx, dy in self.obtenir_directions(piece):
            x1, y1 = piece.ligne + dx, piece.col + dy
            if 0 <= x1 < TAILLE_PLATEAU and 0 <= y1 < TAILLE_PLATEAU and self.plateau[x1][y1] is None:
                deplacements.append((x1, y1))
        return deplacements

    def verifier_fin_jeu(self):
        blancs = noirs = 0
        for ligne in self.plateau:
            for piece in ligne:
                if piece:
                    if piece.couleur == 'white':
                        blancs += 1
                    else:
                        noirs += 1
        if blancs == 0:
            self.partie_terminee = True
            audio.arreter_musique()
            return 'Noirs'
        elif noirs == 0:
            self.partie_terminee = True
            audio.arreter_musique()
            return 'Blancs'
        return None

    def changer_joueur(self):
        self.joueur = 'black' if self.joueur == 'white' else 'white'

    def meilleur_coup(self):
        # IA simple: choisit le premier coup possible qui capture sinon le premier coup
        coups_possibles = []
        coups_capture = []
        for ligne in range(TAILLE_PLATEAU):
            for col in range(TAILLE_PLATEAU):
                piece = self.plateau[ligne][col]
                if piece and piece.couleur == self.joueur:
                    coups = self.obtenir_deplacements_valides(piece)
                    for coup in coups:
                        # Vérifier si c'est une capture
                        if abs(coup[0] - ligne) == 2:
                            coups_capture.append((piece, coup))
                        else:
                            coups_possibles.append((piece, coup))
        if coups_capture:
            return coups_capture[0]
        if coups_possibles:
            return coups_possibles[0]
        return None, None

class InterfaceJeu:
    def __init__(self, root):
        self.root = root
        self.root.title("Le Jeu de dames des Miashs")
        self.fullscreen = False

        self.label_titre = tk.Label(root, text="Le Jeu de dames des Miashs", font=("Arial", 24, "bold"), fg="white", bg="#2e2e2e")
        self.label_titre.pack(side=tk.TOP, fill=tk.X)

        self.canvas = tk.Canvas(root, bg="#2e2e2e")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.jeu = None
        self.selection = None
        self.aide_active = False
        self.mode_ia = False  # Mode IA activé ou non

        self.btn_1vs1 = tk.Button(root, text="1 vs 1", font=("Arial", 18), command=self.lancer_1vs1)
        self.btn_ia = tk.Button(root, text="1 vs IA", font=("Arial", 18), command=self.lancer_1vsIA)
        self.btn_aide = tk.Button(root, text=f"Aide ({NB_AIDES_PAR_JOUEUR})", font=("Arial", 14), command=self.utiliser_aide, state=tk.DISABLED)

        self.canvas.bind("<Button-1>", self.clic_souris)
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.exit_fullscreen)
        self.root.protocol("WM_DELETE_WINDOW", self.fermer_jeu)
        self.root.bind("<Configure>", self.redessiner)

        self.label_info = tk.Label(root, text="", font=("Arial", 12), fg="white", bg="#2e2e2e", justify="left")
        self.label_info.place(relx=0.98, rely=0.02, anchor='ne')

        self.label_aide_white = tk.Label(root, text="", font=("Arial", 12), fg="white", bg="#2e2e2e", justify="left")
        self.label_aide_white.place(relx=0.01, rely=0.9, anchor='w')
        self.label_aide_black = tk.Label(root, text="", font=("Arial", 12), fg="white", bg="#2e2e2e", justify="left")
        self.label_aide_black.place(relx=0.98, rely=0.9, anchor='e')

        self.canvas_capture_white = tk.Canvas(root, width=150, height=TAILLE_PLATEAU * 20, bg="#222222")
        self.canvas_capture_black = tk.Canvas(root, width=150, height=TAILLE_PLATEAU * 20, bg="#444444")

        self.page_accueil()

    def page_accueil(self):
        self.canvas.delete("all")
        largeur = self.canvas.winfo_width() or 640
        hauteur = self.canvas.winfo_height() or 480
        self.canvas.create_text(largeur // 2, hauteur // 4, text="Bienvenue !", font=("Arial", 24), fill="white", justify="center")
        self.btn_1vs1.place(relx=0.5, rely=0.5, anchor='center')
        self.btn_ia.place(relx=0.5, rely=0.6, anchor='center')

    def lancer_1vs1(self):
        self.mode_ia = False
        self.jeu = JeuDeDames()
        self.selection = None
        self.aide_active = False
        self.btn_aide.config(state=tk.NORMAL, text=f"Aide ({NB_AIDES_PAR_JOUEUR})")
        self.btn_aide.place(relx=0.9, rely=0.95, anchor='center')
        self.btn_1vs1.place_forget()
        self.btn_ia.place_forget()
        self.canvas_capture_white.place(relx=0.01, rely=0.1, anchor='nw')
        self.canvas_capture_black.place(relx=0.99, rely=0.1, anchor='ne')
        self.redessiner()

    def lancer_1vsIA(self):
        self.mode_ia = True
        self.jeu = JeuDeDames()
        self.selection = None
        self.aide_active = False
        self.btn_aide.config(state=tk.NORMAL, text=f"Aide ({NB_AIDES_PAR_JOUEUR})")
        self.btn_aide.place(relx=0.9, rely=0.95, anchor='center')
        self.btn_1vs1.place_forget()
        self.btn_ia.place_forget()
        self.canvas_capture_white.place(relx=0.01, rely=0.1, anchor='nw')
        self.canvas_capture_black.place(relx=0.99, rely=0.1, anchor='ne')
        self.redessiner()
        # Si c'est au tour de l'IA (noir) de jouer au début, on lance le coup IA
        if self.jeu.joueur == 'black':
            self.jouer_coup_ia()

    def redessiner(self, event=None):
        self.canvas.delete("all")
        if not self.jeu:
            return
        largeur = self.canvas.winfo_width()
        hauteur = self.canvas.winfo_height()
        self.case_taille = min((largeur - 320) // TAILLE_PLATEAU, (hauteur - 60) // TAILLE_PLATEAU)
        decal_x = (largeur - self.case_taille * TAILLE_PLATEAU) // 2
        decal_y = (hauteur - self.case_taille * TAILLE_PLATEAU) // 2 + 30  # Décalage pour laisser place au titre

        # Dessiner le plateau
        for ligne in range(TAILLE_PLATEAU):
            for col in range(TAILLE_PLATEAU):
                x1 = decal_x + col * self.case_taille
                y1 = decal_y + ligne * self.case_taille
                x2 = x1 + self.case_taille
                y2 = y1 + self.case_taille
                couleur_case = "#b58863" if (ligne + col) % 2 == 1 else "#f0d9b5"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=couleur_case, outline="black")

        # Dessiner les pièces
        for ligne in range(TAILLE_PLATEAU):
            for col in range(TAILLE_PLATEAU):
                piece = self.jeu.plateau[ligne][col]
                if piece:
                    x = decal_x + col * self.case_taille + self.case_taille // 2
                    y = decal_y + ligne * self.case_taille + self.case_taille // 2
                    rayon = self.case_taille // 2 - 4
                    couleur = "white" if piece.couleur == 'white' else "black"
                    self.canvas.create_oval(x - rayon, y - rayon, x + rayon, y + rayon, fill=couleur, outline="gold", width=2 if piece.dame else 1)
                    if piece.dame:
                        self.canvas.create_text(x, y, text="D", fill="gold", font=("Arial", rayon, "bold"))

        # Afficher la sélection
        if self.selection:
            ligne, col = self.selection
            x1 = decal_x + col * self.case_taille
            y1 = decal_y + ligne * self.case_taille
            x2 = x1 + self.case_taille
            y2 = y1 + self.case_taille
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="red", width=3)

        # Afficher les aides si activée
        if self.aide_active and self.selection:
            ligne, col = self.selection
            piece = self.jeu.plateau[ligne][col]
            if piece and piece.couleur == self.jeu.joueur:
                coups = self.jeu.obtenir_deplacements_valides(piece)
                for (lx, ly) in coups:
                    x1 = decal_x + ly * self.case_taille + self.case_taille // 4
                    y1 = decal_y + lx * self.case_taille + self.case_taille // 4
                    x2 = x1 + self.case_taille // 2
                    y2 = y1 + self.case_taille // 2
                    self.canvas.create_oval(x1, y1, x2, y2, outline="blue", width=3)

        # Mise à jour des pièces capturées
        self.afficher_pieces_capturees()

        # Affichage des infos
        self.label_info.config(text=f"Tour du joueur : {'Blancs' if self.jeu.joueur == 'white' else 'Noirs'}")

        # Affichage aides restantes
        self.label_aide_white.config(text=f"Aides Blancs : {self.jeu.aides_restantes['white']}")
        self.label_aide_black.config(text=f"Aides Noirs : {self.jeu.aides_restantes['black']}")

    def afficher_pieces_capturees(self):
        self.canvas_capture_white.delete("all")
        self.canvas_capture_black.delete("all")

        y = 10
        for piece in self.jeu.pieces_capturees['white']:
            couleur = "white"
            self.canvas_capture_white.create_oval(10, y, 30, y + 20, fill=couleur)
            y += 25

        y = 10
        for piece in self.jeu.pieces_capturees['black']:
            couleur = "black"
            self.canvas_capture_black.create_oval(10, y, 30, y + 20, fill=couleur)
            y += 25

    def clic_souris(self, event):
        if not self.jeu or self.jeu.partie_terminee:
            return

        x = event.x
        y = event.y
        largeur = self.canvas.winfo_width()
        hauteur = self.canvas.winfo_height()
        decal_x = (largeur - self.case_taille * TAILLE_PLATEAU) // 2
        decal_y = (hauteur - self.case_taille * TAILLE_PLATEAU) // 2 + 30

        col = (x - decal_x) // self.case_taille
        ligne = (y - decal_y) // self.case_taille
        if 0 <= ligne < TAILLE_PLATEAU and 0 <= col < TAILLE_PLATEAU:
            piece = self.jeu.plateau[ligne][col]
            if self.selection:
                piece_sel = self.jeu.plateau[self.selection[0]][self.selection[1]]
                if self.jeu.deplacer(piece_sel, ligne, col):
                    self.selection = None
                    self.aide_active = False
                    gagnant = self.jeu.verifier_fin_jeu()
                    if gagnant:
                        messagebox.showinfo("Fin de partie", f"Le joueur {gagnant} a gagné !")
                        self.jeu.partie_terminee = True
                        return
                    self.jeu.changer_joueur()
                    self.redessiner()
                    if self.mode_ia and self.jeu.joueur == 'black':
                        self.root.after(500, self.jouer_coup_ia)
                    return
                else:
                    # Sélectionne une autre pièce si c'est la bonne couleur
                    if piece and piece.couleur == self.jeu.joueur:
                        self.selection = (ligne, col)
                        self.aide_active = True
                        self.redessiner()
                    else:
                        # Clic invalide, on désélectionne
                        self.selection = None
                        self.aide_active = False
                        self.redessiner()
            else:
                if piece and piece.couleur == self.jeu.joueur:
                    self.selection = (ligne, col)
                    self.aide_active = False
                    self.redessiner()

    def utiliser_aide(self):
        if not self.selection:
            messagebox.showwarning("Aide", "Sélectionnez une pièce avant d'utiliser l'aide.")
            return
        if self.jeu.aides_restantes[self.jeu.joueur] <= 0:
            messagebox.showwarning("Aide", "Plus d'aides disponibles pour ce joueur.")
            return
        self.aide_active = True
        self.jeu.aides_restantes[self.jeu.joueur] -= 1
        self.btn_aide.config(text=f"Aide ({self.jeu.aides_restantes[self.jeu.joueur]})")
        self.redessiner()

    def jouer_coup_ia(self):
        piece, coup = self.jeu.meilleur_coup()
        if piece and coup:
            self.jeu.deplacer(piece, coup[0], coup[1])
            gagnant = self.jeu.verifier_fin_jeu()
            if gagnant:
                messagebox.showinfo("Fin de partie", f"Le joueur {gagnant} a gagné !")
                self.jeu.partie_terminee = True
                return
            self.jeu.changer_joueur()
            self.redessiner()
        else:
            messagebox.showinfo("Fin de partie", "L'IA ne peut plus jouer. Partie terminée.")
            self.jeu.partie_terminee = True

    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)

    def exit_fullscreen(self, event=None):
        self.fullscreen = False
        self.root.attributes("-fullscreen", False)

    def fermer_jeu(self):
        if messagebox.askokcancel("Quitter", "Voulez-vous quitter le jeu ?"):
            audio.arreter_musique()
            self.root.destroy()

def main():
    root = tk.Tk()
    root.configure(bg="#2e2e2e")
    interface = InterfaceJeu(root)
    root.mainloop()

if __name__ == "__main__":
    main()


# copyright Anass.M, Anasse.B Et Taha Turkan



