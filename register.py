# cette partie gère l'affichage de la fenêtre d'inscription
# Fara mohamed pour SI-CA1 (projet Python) - 2025-2026
# 29 avril 2026
# register.py : affichage de la fenêtre d'inscription

import tkinter as tk
from model import check_register
from tkinter import messagebox
from utils.session import Session



def show_register(parent, db_mode="local"):
    if Session.is_authenticated():
        messagebox.showinfo("Info", f"Déjà connecté en tant que {Session.pseudo}")
        return
    win = tk.Toplevel(parent)
    win.title("Inscription")

    # Empêcher d'interagir avec parent
    win.transient(parent)   # attache au parent
    win.grab_set()          # rend la fenêtre modale

    tk.Label(win, text="Pseudo").grid(row=0, column=0)
    tk.Label(win, text="Mot de passe").grid(row=1, column=0, padx=20, pady=20)

    entry_pseudo = tk.Entry(win)
    entry_pseudo.grid(row=0, column=1)

    entry_pass = tk.Entry(win, show="*")
    entry_pass.grid(row=1, column=1, padx=20, pady=20)

    def do_register():
        result= check_register(entry_pseudo.get(), entry_pass.get(), db_mode)
        if result == "OK":
            messagebox.showinfo("OK", f"Inscription réussie pour {entry_pseudo.get()} ! Vous pouvez maintenant vous connecter.")
            win.destroy()
        elif result == "EXISTS":
            messagebox.showerror("Erreur", "Ce pseudo est déjà pris, veuillez en choisir un autre.")
        else:
            messagebox.showerror("Erreur", "Une erreur est survenue lors de l'inscription. Veuillez réessayer.")

    tk.Button(win, text="S'inscrire", command=do_register).grid(row=2, columnspan=2)
