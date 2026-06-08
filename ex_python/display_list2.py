# afficher une liste
# JCY avril 2026
# dans cet exemple on donne seulement les données sous forme d'un dictionnaire
# et on peut trier par colonne

import tkinter as tk
from tkinter import ttk



# -------- Exemple d'utilisation ---------

result = [
    {"id": 1, "name": "Rock Legends Night", "date":"2026-03-10"},
    {"id": 2, "name": "Jazz Evening", "date":"2026-03-10"},
    {"id": 10, "name": "Classical Gala", "date":"2026-03-10"},
    {"id": 3, "name": "Electro Party", "date":"2026-03-10"},
]



def display_array(frame, data):
    # nettoyer
    for widget in frame.winfo_children():
        widget.destroy()

    columns = list(data[0].keys()) #on prend les titres dans la première ligne de données

    tree = ttk.Treeview(frame, columns=columns, show="headings")

    # colonnes
    for col in columns:
        tree.heading(col, text=col, command=lambda c=col: sort_by_column(tree, c, data, columns))
        tree.column(col, anchor="center")

    # affichage initial
    insert_rows(tree, data, columns)

    tree.pack(fill="both", expand=True)


def insert_rows(tree, data, columns):
    """Efface et réaffiche toutes les lignes avec renumérotation automatique."""
    # supprimer anciennes lignes
    for row in tree.get_children():
        tree.delete(row)

    # recréer les lignes
    for idx, row in enumerate(data, start=1):
        values = []
        for col in columns :
            values.append(row[col])
        #values = [row[col] for col in columns] #version plus compacte
        tree.insert("", tk.END, values=values)


def sort_by_column(tree, col, data, columns):
    """Trie les données puis réaffiche le tableau."""
    # détecter tri ascendant/descendant
    descending = getattr(tree, "sort_desc_"+col, False)
    setattr(tree, "sort_desc_"+col, not descending)

    data.sort(key=lambda r: r[col], reverse=descending)

    # réaffichage
    insert_rows(tree, data, columns)



win = tk.Tk()
lbl_title =tk.Label(win,text="Exemple de tableau automatique", font=("Arial",20))
lbl_title.pack()
frame = tk.Frame(win)
frame.pack(fill="both", expand=True)

# appel de l'affichage d'une liste dans le treeview
display_array(frame, result)

win.mainloop()
