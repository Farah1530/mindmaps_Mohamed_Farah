# Exemple d'appel de foncion lambda par un treeview (avec menu contextuel)
# JCY pour SI-CA1a
# 16.05.26

import tkinter as tk
from tkinter import ttk, messagebox
import random
import math


# -----------------------------
# Functions called by the menu
# -----------------------------

def show_square(selected_value):
    if selected_value is not None:
        messagebox.showinfo("Square", f"The square of {selected_value} is {selected_value ** 2}"
        )


def show_square_root(selected_value):
    if selected_value is not None:
        messagebox.showinfo("Square Root", f"The square root of {selected_value} is {math.sqrt(selected_value):2f}"
        )


# -----------------------------
# Right click handler
# -----------------------------


def on_right_click(event):
    # si on veut obtenir la valeur exacte cliquée
    item_id = tree.identify_row(event.y) # renvoie I001 à I003
    print(item_id)
    column_id = tree.identify_column(event.x) # renvoie #1 à #3
    print(column_id)

    if item_id and column_id:

        values = tree.item(item_id, "values") #renvoie la ligne cliquée ("1","9","13")
        print(values)
        column_index = int(column_id.replace("#", "")) - 1 # donne l'index de 0 à 2
        value = int(values[column_index]) # donne la valeur cliquée

        # Important : recréer le menu avec la valeur cliquée
        menu.delete(0, tk.END)
        menu.add_command(
            label="Show square",
            command=lambda v=value: show_square(v)
        )
        menu.add_command(
            label="Show square root",
            command=lambda v=value: show_square_root(v)
        )
        menu.tk_popup(event.x_root, event.y_root)

def on_right_click_first_column(event):
    item_id = tree.identify_row(event.y) # renvoie I001 à I003

    if item_id:
        values = tree.item(item_id, "values")  # toute la ligne

        value = int(values[0])  # ✅ première colonne uniquement

        menu.delete(0, tk.END)

        menu.add_command(
            label="Show square (col 1)",
            command=lambda v=value: show_square(v)
        )

        menu.add_command(
            label="Show square root (col 1)",
            command=lambda v=value: show_square_root(v)
        )

        menu.tk_popup(event.x_root, event.y_root)

# -----------------------------
# Main window
# -----------------------------

window = tk.Tk()
window.title("TreeView Example")

# Variable used by the menu functions
selected_value = None

# -----------------------------
# TreeView
# -----------------------------
tree = ttk.Treeview(
    window,
    columns=("A", "B", "C"),
    show="headings",
    height=3
)

tree.heading("A", text="A")
tree.heading("B", text="B")
tree.heading("C", text="C")

# Insert random values
for _ in range(3):

    row_values = (
        random.randint(1, 20),
        random.randint(1, 20),
        random.randint(1, 20)
    )

    tree.insert("", tk.END, values=row_values)

tree.pack(padx=10, pady=10)

# -----------------------------
# Context menu
# -----------------------------

menu = tk.Menu(window, tearoff=0)

menu.add_command(
    label="Show square",
    command=show_square
)

menu.add_command(
    label="Show square root",
    command=show_square_root
)

# Right click binding(à choisir lequel est le mieux)
tree.bind("<Button-3>", on_right_click_first_column)
# tree.bind("<Button-3>", on_right_click_first_column)

window.mainloop()
