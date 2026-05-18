# Exemple d'appel de foncion lambda par 9 boutons
# JCY pour SI-CA1a
# 16.05.26

import tkinter as tk
from tkinter import messagebox

def case_cliquee(ligne, colonne):
    messagebox.showinfo("Clic",f"Vous avez cliqué sur la case ({ligne}, {colonne})")


win = tk.Tk()
win.title("Mini morpion")

for ligne in range(3):
    for colonne in range(3):
        # la fonction lambda permet de passer des paramètres
        # on les affecte entre le mot lambda et les :
        # parce que les variables ligne et colonne sont "mouvantes"
        bouton = tk.Button(win, text=f"{ligne}{colonne} ",
            width=8, height=4,
            command=lambda l=ligne, c=colonne: case_cliquee(l, c)
        )

        bouton.grid(row=ligne, column=colonne,padx=10, pady=10)

win.mainloop()