# Projet mindmaps : prototype d'affichage de mindmap en radial et forum 
# Farah MOHAMED SI-CA1 (projet Python) - 2025-2026
# 13 avril 2026
# login.py : affichage de la fenêtre de connexion

import tkinter as tk
from tkinter import messagebox
from model import check_login
from utils.session import Session

def show_login(parent, db_mode="local"):
    # si déjà connecté, pas besoin de se reconnecter
    if Session.is_authenticated():
        messagebox.showinfo("Info", f"Déjà connecté en tant que {Session.pseudo}")
        return

    win = tk.Toplevel(parent)
    win.title("Login")

    # empêcher d'interagir avec la fenêtre principale pendant le login
    win.transient(parent)
    win.grab_set()

    tk.Label(win, text="Pseudo").grid(row=0, column=0, padx=20, pady=10)
    tk.Label(win, text="Mot de passe").grid(row=1, column=0, padx=20, pady=10)

    entry_pseudo = tk.Entry(win)
    entry_pseudo.grid(row=0, column=1, padx=20, pady=10)

    entry_pass = tk.Entry(win, show="*")
    entry_pass.grid(row=1, column=1, padx=20, pady=10)

    def attempt_login(db_mode=db_mode):
        user = check_login(entry_pseudo.get(), entry_pass.get(), db_mode)

        if user:
            # stocker le pseudo, le level et l'id dans la session
            Session.login(user["pseudo"], user["level"], user["id"])
            win.destroy()
        else:
            messagebox.showerror("Erreur", "Login incorrect")

    tk.Button(win, text="Se connecter", command=attempt_login).grid(row=2, column=0, columnspan=2, pady=10)

    # empêche d'accéder à la fenêtre principale tant que login est ouvert
    parent.wait_window(win)