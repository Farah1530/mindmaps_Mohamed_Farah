# afficher une liste
# JCY avril 2026
# dans cet exemple on donne les columns puis les données

import tkinter as tk
from tkinter import ttk


# test de la fonction
result = [
    {"id": 1, "name": "Rock Legends Night"},
    {"id": 2, "name": "Jazz Evening"},
]

columns = ["id", "name"]

def display_array(frame, data, columns):
    # affiche un tableau avec colonnes et valeurs
    # nettoyer
    for widget in frame.winfo_children():
        widget.destroy()

    tree = ttk.Treeview(frame, columns=columns, show="headings")
    tree.pack(fill="both", expand=True)
    
    # colonnes
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center")
    
    # lignes (correction ici)
    for row in data:
        val= [row[col] for col in columns]
        tree.insert("", tk.END, values=val)




# interface graphique

win = tk.Tk()
frame = tk.Frame(win)
frame.pack()

display_array(frame, result, columns)

win.mainloop()

