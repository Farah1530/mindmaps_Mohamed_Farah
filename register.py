# cette partie gère l'affichage de la fenêtre d'inscription
# Farah MOHAMED pour SI-CA1 (projet Python) - 2025-2026
# 29 avril 2026
# register.py : affichage de la fenêtre d'inscription

import tkinter as tk
from model import check_register
from tkinter import messagebox
from utils.session import Session


def show_register(parent, db_mode="local"):
    # si déjà connecté, pas besoin de s'inscrire
    if Session.is_authenticated():
        messagebox.showinfo("Info", f"Déjà connecté en tant que {Session.pseudo}")
        return

    win = tk.Toplevel(parent)
    win.title("Inscription")

    # empêcher d'interagir avec la fenêtre principale pendant l'inscription
    win.transient(parent)
    win.grab_set()

    # champ pseudo
    tk.Label(win, text="Pseudo").grid(row=0, column=0, padx=20, pady=10)
    entry_pseudo = tk.Entry(win)
    entry_pseudo.grid(row=0, column=1, padx=20, pady=10)

    # champ mot de passe
    tk.Label(win, text="Mot de passe").grid(row=1, column=0, padx=20, pady=10)
    entry_pass = tk.Entry(win, show="*")
    entry_pass.grid(row=1, column=1, padx=20, pady=10)

    # champ confirmation mot de passe (nouveau)
    tk.Label(win, text="Confirmer mot de passe").grid(row=2, column=0, padx=20, pady=10)
    entry_pass_confirm = tk.Entry(win, show="*")
    entry_pass_confirm.grid(row=2, column=1, padx=20, pady=10)

    # champ couleur (nouveau) — l'utilisateur choisit sa couleur pour ses nœuds
    tk.Label(win, text="Couleur (ex: lightblue)").grid(row=3, column=0, padx=20, pady=10)
    entry_color = tk.Entry(win)
    entry_color.insert(0, "white")  # valeur par défaut
    entry_color.grid(row=3, column=1, padx=20, pady=10)

    def do_register():
        pseudo = entry_pseudo.get().strip()       # .strip() enlève les espaces avant/après
        password = entry_pass.get()
        password_confirm = entry_pass_confirm.get()
        color = entry_color.get().strip()

        # vérifier que le pseudo n'est pas vide
        if not pseudo:
            messagebox.showerror("Erreur", "Le pseudo ne peut pas être vide")
            return

        # vérifier que le mot de passe n'est pas vide
        if not password:
            messagebox.showerror("Erreur", "Le mot de passe ne peut pas être vide")
            return

        # vérifier que les deux mots de passe sont identiques
        if password != password_confirm:
            messagebox.showerror("Erreur", "Les mots de passe ne correspondent pas")
            return

        # tout est ok, on essaie d'insérer en BD
        result = check_register(pseudo, password, color, db_mode)

        if result == "OK":
            messagebox.showinfo("OK", f"Inscription réussie pour {pseudo} ! Vous pouvez maintenant vous connecter.")
            win.destroy()
        elif result == "EXISTS":
            messagebox.showerror("Erreur", "Ce pseudo est déjà pris, veuillez en choisir un autre.")
        else:
            messagebox.showerror("Erreur", "Une erreur est survenue lors de l'inscription. Veuillez réessayer.")

    tk.Button(win, text="S'inscrire", command=do_register).grid(row=4, columnspan=2, pady=10)