# prototype d'affichage de mindmap en radial et forum   
# Farah MOHAMED SI-CA1 (projet Python) - 2025-2026 -v0.1
# 13 avril 2026
# main.py : affichage de la fenêtre principale, gestion de la connexion et des différentes vues (tables + mindmap)

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox, simpledialog
from login import show_login
from register import show_register
from tree_display import display_array
from utils.session import Session
import math
# un seul import depuis model (correction du double import)
from model import get_maps, get_nodes_for_map, get_users, get_nodes, update_node_text, delete_node, insert_node, insert_map, update_map_title, delete_map

# variable globale pour le mode DB (local ou remote)
db_mode = None
current_map_id = None

# vérification de connexion — retourne True si connecté, False sinon
def check_auth():
    return Session.is_authenticated()

# affichage des maps dans le treeview de gauche
def display_maps():
    result = get_maps(db_mode)
    frm_result.tree = display_array(frm_result, result)
    frm_result.tree.bind("<Double-1>", on_map_double_click)  # double clic pour afficher le mindmap
    frm_result.tree.bind("<Button-3>", on_map_right_click)   # clic droit pour le menu contextuel

# afficher les users dans le treeview de gauche
def display_users():
    result = get_users(db_mode)
    frm_result.tree = display_array(frm_result, result)
    frm_result.tree.bind("<Double-1>", on_user_double_click)

# afficher les nodes dans le treeview de gauche
def display_nodes():
    result = get_nodes(db_mode)
    frm_result.tree = display_array(frm_result, result)
    # pas de double clic sur les nodes (correction du bug on_node_double_click)

# double clic sur une map : affiche le mindmap dans right_frame
def on_map_double_click(event):
    selected = frm_result.tree.selection()
    if selected:
        item = frm_result.tree.item(selected[0])
        values = item['values']
        map_id = values[0]  # première colonne = id
        display_mindmap(map_id)

# double clic sur un user : affiche son profil dans right_frame
def on_user_double_click(event):
    selected = frm_result.tree.selection()
    if selected:
        item = frm_result.tree.item(selected[0])
        values = item['values']
        user_id = values[0]  # première colonne = id
        display_user_profile(user_id)

# clic droit sur la liste des maps : affiche un menu contextuel
def on_map_right_click(event):
    # trouver sur quelle ligne du treeview on a fait clic droit
    item_id = frm_result.tree.identify_row(event.y)

    # créer un menu vide (tearoff=0 = pas de trait en haut du menu)
    map_menu = tk.Menu(root, tearoff=0)

    # "Insérer un nouveau map" est toujours disponible, même si on clique dans le vide
    map_menu.add_command(label="Insérer un nouveau map", command=create_map_action)

    # si on a cliqué sur une ligne existante (pas dans le vide)
    if item_id:
        # sélectionner visuellement la ligne cliquée
        frm_result.tree.selection_set(item_id)

        # récupérer les valeurs de la ligne (id, title, author_id)
        values = frm_result.tree.item(item_id, "values")
        map_id = values[0]    # première colonne = id
        map_title = values[1] # deuxième colonne = titre

        # ajouter Editer le titre et Supprimer seulement si une ligne est sélectionnée
        map_menu.add_command(label="Editer le titre", command=lambda: rename_map_action(map_id, map_title))
        map_menu.add_command(label="Supprimer", command=lambda: delete_map_action(map_id, map_title))

    # afficher le menu exactement là où on a cliqué sur l'écran
    map_menu.tk_popup(event.x_root, event.y_root)


# créer une nouvelle map avec un nœud racine automatique
def create_map_action():
    # vérifier que l'utilisateur est connecté
    if not check_auth():
        messagebox.showerror("Erreur", "Vous devez être connecté pour créer une map")
        return

    # demander le titre de la nouvelle map
    title = simpledialog.askstring("Nouvelle map", "Titre de la nouvelle map :")

    if title:
        # créer la map et récupérer son id
        new_map_id = insert_map(title, Session.id, db_mode)
        # créer automatiquement le nœud racine (parent_id=None, level=0)
        insert_node(
            map_id=new_map_id,
            parent_id=None,    # pas de parent = c'est la racine
            author_id=Session.id,
            text=title,        # le texte de la racine = le titre de la map
            level=0,           # niveau 0 = racine
            db_mode=db_mode
        )
        display_maps()  # rafraîchir la liste pour voir la nouvelle map


# renommer une map existante
def rename_map_action(map_id, old_title):
    # vérifier que l'utilisateur est connecté
    if not check_auth():
        messagebox.showerror("Erreur", "Vous devez être connecté")
        return

    # demander le nouveau titre en pré-remplissant avec l'ancien
    new_title = simpledialog.askstring("Renommer", "Nouveau titre :", initialvalue=old_title)

    # modifier seulement si l'utilisateur a écrit quelque chose de différent
    if new_title and new_title != old_title:
        update_map_title(map_id, new_title, db_mode)
        display_maps()


# supprimer une map et tous ses nœuds
def delete_map_action(map_id, map_title):
    # vérifier que l'utilisateur est connecté
    if not check_auth():
        messagebox.showerror("Erreur", "Vous devez être connecté")
        return

    # demander confirmation avant de supprimer (action irréversible)
    confirm = messagebox.askyesno("Supprimer", f"Supprimer la map '{map_title}' et tous ses nœuds ?")

    if confirm:
        delete_map(map_id, db_mode)

        global current_map_id
        # si la map supprimée était celle affichée à droite, nettoyer la zone
        if current_map_id == int(map_id):
            current_map_id = None
            for widget in right_frame.winfo_children():
                widget.destroy()
            tk.Label(right_frame, text="Zone Mindmap", font=("Arial", 16)).pack(expand=True)

        display_maps()

# affichage du mindmap en mode radial avec canvas (utilisation de l'IA)
def display_mindmap_radial(frame, nodes):
    container = tk.Frame(frame)
    container.pack(fill='both', expand=True)
    canvas = tk.Canvas(container, bg='yellow', width=3000, height=2000)

    vsb = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    hsb = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
    canvas.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True)

    # zoom avec la molette de la souris (utilisation de l'IA)
    def zoom(event):
        factor = 1.1 if event.delta > 0 else 0.9
        canvas.scale("all", event.x, event.y, factor, factor)
        canvas.configure(scrollregion=canvas.bbox("all"))

    canvas.bind("<MouseWheel>", zoom)

    cx, cy = 1500, 1000  # centre du canvas

    positions = {}  # stocke la position (x,y) de chaque node par son id

    # dessine un node et ses enfants de manière récursive (utilisation de l'IA)
    def draw_radial(node, x, y, angle_start, angle_end, level):
        positions[node['id']] = (x, y)
        color = node.get('color', 'red') if level > 0 else 'red'
        canvas.create_oval(x-50, y-50, x+50, y+50, fill=color, outline='red')
        canvas.create_text(x, y, text=node['text'][:15], font=('Arial', 7))

        children = [n for n in nodes if n['parent_id'] == node['id']]
        if not children:
            return

        angle_step = (angle_end - angle_start) / max(len(children), 1)
        for i, child in enumerate(children):
            a = angle_start + angle_step * i + angle_step / 2
            rad = math.radians(a)
            radius = level * 180 + 200
            child_x = x + radius * math.cos(rad)
            child_y = y + radius * math.sin(rad)
            dx = child_x - x
            dy = child_y - y
            dist = math.sqrt(dx*dx + dy*dy)
            offset = 50
            start_x = x + (dx / dist) * offset
            start_y = y + (dy / dist) * offset
            end_x = child_x - (dx / dist) * offset
            end_y = child_y - (dy / dist) * offset
            canvas.create_line(start_x, start_y, end_x, end_y, fill='gray')
            draw_radial(child, child_x, child_y, a - angle_step / 2, a + angle_step / 2, level + 1)

    root_node = next((n for n in nodes if n['parent_id'] is None or n['parent_id'] == 0), None)
    if root_node:
        draw_radial(root_node, cx, cy, 0, 360, 0)

    canvas.configure(scrollregion=canvas.bbox("all"))

# affichage du mindmap selon le mode sélectionné (tree, forum ou radial)
def display_mindmap(map_id):
    global current_map_id
    current_map_id = map_id
    nodes = get_nodes_for_map(map_id, db_mode)

    # nettoyer right_frame avant d'afficher
    for widget in right_frame.winfo_children():
        widget.destroy()

    if nodes:
        mode = display_mode.get()
        if mode == 'tree':
            display_mindmap_tree(right_frame, nodes)
        elif mode == 'forum':
            display_mindmap_forum(right_frame, nodes)
        elif mode == 'radial':
            display_mindmap_radial(right_frame, nodes)
    else:
        tk.Label(right_frame, text="Aucun node pour ce mindmap").pack()

# affichage du profil d'un utilisateur (ses nodes)
def display_user_profile(user_id):
    global current_user_id
    current_user_id = user_id
    nodes = get_nodes(db_mode)

    for widget in right_frame.winfo_children():
        widget.destroy()

    if nodes:
        mode = display_mode.get()
        if mode == 'tree':
            display_mindmap_tree(right_frame, nodes)
        elif mode == 'forum':
            display_mindmap_forum(right_frame, nodes)
    else:
        tk.Label(right_frame, text="Aucun node pour cet utilisateur").pack()

# rafraîchir le mindmap actuellement affiché
def refresh_mindmap():
    if current_map_id is not None:
        display_mindmap(current_map_id)

# affichage du mindmap en TreeView (arbre dépliable)
def display_mindmap_tree(frame, nodes):
    tree = ttk.Treeview(frame, columns=(), show='tree')
    tree.heading('#0', text='Text')

    style = ttk.Style()
    style.configure("Right.Treeview", font=("TkDefaultFont", 20), rowheight=35)
    tree.configure(style="Right.Treeview")

    # fonction récursive pour insérer les nodes dans le treeview
    def insert_nodes(parent, parent_id=None):
        for node in nodes:
            if node['parent_id'] == parent_id:
                item = tree.insert(parent, 'end', text=node['text'])
                insert_nodes(item, node['id'])

    insert_nodes('')

    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    tree.pack(side='left', fill='both', expand=True)
    vsb.pack(side='right', fill='y')
    hsb.pack(side='bottom', fill='x')

# affichage du mindmap en forum (rectangles imbriqués avec scrollbars)
def display_mindmap_forum(frame, nodes):
    container = tk.Frame(frame)
    container.pack(fill='both', expand=True)

    canvas = tk.Canvas(container, bg='white')
    vsb = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    hsb = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
    canvas.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True)

    def update_scroll_region(event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))

    canvas.bind("<Configure>", update_scroll_region)

    # trouver le nœud racine (celui sans parent)
    root_node = next((n for n in nodes if n['parent_id'] is None or n['parent_id'] == 0), None)
    if not root_node:
        return

    canvas_width = 800
    node_height = 25

    # crée un rectangle avec des coins arrondis sur le canvas
    def create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=10, **kwargs):
        radius = min(radius, abs(x2 - x1)//2, abs(y2 - y1)//2)
        points = [x1 + radius, y1, x2 - radius, y1,
            x2, y1, x2, y1 + radius,
            x2, y2 - radius, x2, y2,
            x2 - radius, y2, x1 + radius, y2,
            x1, y2, x1, y2 - radius,
            x1, y1 + radius, x1, y1,
            x1 + radius, y1]
        return canvas.create_polygon(points, smooth=True, **kwargs)

    # place les nodes de manière récursive (chaque enfant est décalé vers la droite)
    def place_forum(node, x, y, width_percent, level=0):
        width = int(canvas_width * width_percent / 100)
        item = create_rounded_rectangle(canvas, x, y, x + width, y + node_height, radius=8,
            fill='lightblue' if level == 0 else node["color"], outline='black')
        canvas.create_text(x + width/2, y + node_height/2, text=node['text'][:20], anchor='center', font=("Arial", 12))
        # clic droit sur le node pour éditer
        canvas.tag_bind(item, "<Button-3>", lambda e, n=node: edit_node(e, n))
        children = [n for n in nodes if n['parent_id'] == node['id']]
        total_height = node_height + 10
        if children:
            child_x = x + int(canvas_width * 20 / 100)
            child_width_percent = max(width_percent - 5, 10)
            current_y = y + node_height + 10
            for child in children:
                child_height = place_forum(child, child_x, current_y, child_width_percent, level+1)
                current_y += child_height
                total_height += child_height
        return total_height

    place_forum(root_node, 20, 20, 50)
    update_scroll_region()

# affiche un menu contextuel sur un node (éditer, supprimer, insérer en dessous)
def edit_node(event, node):
    # si personne n'est connecté, on ne fait rien
    if not check_auth():
        return
    menu = tk.Menu(root, tearoff=0)
    menu.add_command(label="Éditer", command=lambda: edit_text(node))
    menu.add_command(label="Supprimer", command=lambda: delete_node_action(node))
    menu.add_command(label="Insérer en dessous", command=lambda: insert_below(node))
    menu.post(event.x_root, event.y_root)

# éditer le texte d'un node (seulement si on est l'auteur)
def edit_text(node):
    if not check_auth():
        messagebox.showerror("Erreur", "Vous devez être connecté")
        return
    if node["author_id"] != Session.id:
        messagebox.showerror("Erreur", "Vous ne pouvez modifier que vos propres nœuds")
        return
    new_text = simpledialog.askstring("Éditer", "Nouveau texte :", initialvalue=node["text"])
    if new_text:
        update_node_text(node["id"], new_text, db_mode)
        refresh_mindmap()

# supprimer un node (seulement si on est l'auteur)
def delete_node_action(node):
    if not check_auth():
        messagebox.showerror("Erreur", "Vous devez être connecté")
        return
    if node["author_id"] != Session.id:
        messagebox.showerror("Erreur", "Vous ne pouvez supprimer que vos propres nœuds")
        return
    confirm = messagebox.askyesno("Supprimer", f"Supprimer le nœud '{node['text']}' ?")
    if confirm:
        delete_node(node["id"], db_mode)
        refresh_mindmap()

# insérer un nouveau node enfant en dessous du node sélectionné
def insert_below(node):
    if not check_auth():
        messagebox.showerror("Erreur", "Vous devez être connecté")
        return
    new_text = simpledialog.askstring("Insérer", "Texte du nouveau nœud :")
    if new_text:
        insert_node(
            map_id=current_map_id,
            parent_id=node["id"],       # le parent = le node sur lequel on a cliqué
            author_id=Session.id,
            text=new_text,
            level=node["level"] + 1,    # level = level du parent + 1
            db_mode=db_mode
        )
        refresh_mindmap()

# changer le mode DB (local ou remote) et rafraîchir la liste des maps
def set_db_mode(mode):
    global db_mode
    if mode != db_mode:
        db_mode = mode
        lbl_user.config(text="Non connecté")
        lbl_db_mode.config(text=f"Mode DB: {db_mode}", bg="red" if db_mode == "remote" else "green", fg="white")
        display_maps()

# ouvrir la fenêtre de login
def login():
    show_login(root, db_mode)
    if Session.is_authenticated():
        # afficher le pseudo ET le level (correction bug test 13)
        lbl_user.config(text=f"Connecté en tant que {Session.pseudo} / {Session.level}")

# ouvrir la fenêtre de register
def register():
    show_register(root, db_mode)
    if Session.is_authenticated():
        lbl_user.config(text=f"Connecté en tant que {Session.pseudo} / {Session.level}")

# déconnecter l'utilisateur (correction bug test 15)
def logout():
    Session.logout()
    lbl_user.config(text="Non connecté")


# fenêtre principale
root = tk.Tk()
root.minsize(1600, 1200)
root.state('zoomed')
root.title("Mindmaps - Farah MOHAMED v1.0")

# création du menu principal
menubar = tk.Menu(root)

# menu Afficher
display_menu = tk.Menu(menubar, tearoff=0)
display_menu.add_command(label="Maps", command=display_maps)
display_menu.add_command(label="Users", command=display_users)
display_menu.add_command(label="Nodes", command=display_nodes)
menubar.add_cascade(label="Afficher", menu=display_menu)

# menu Login/Register
login_menu = tk.Menu(menubar, tearoff=0)
login_menu.add_command(label="Login", command=login)
login_menu.add_command(label="Register", command=register)
login_menu.add_command(label="Logout", command=logout)
menubar.add_cascade(label="Login/Register", menu=login_menu)

# menu local/remote
db_menu = tk.Menu(menubar, tearoff=0)
db_menu.add_command(label="Local", command=lambda: set_db_mode('local'))
db_menu.add_command(label="Remote", command=lambda: set_db_mode('remote'))
menubar.add_cascade(label="Mode DB", menu=db_menu)

root.config(menu=menubar)

# configuration du grid pour root
root.columnconfigure(0, minsize=500)
root.columnconfigure(1, weight=1)
root.rowconfigure(0, weight=1)

# frame gauche pour la liste et les contrôles
left_frame = tk.Frame(root, bg="lightgray", width=500)
left_frame.grid(column=0, row=0, sticky="ns")

# frame droite pour l'affichage du mindmap
right_frame = tk.Frame(root, bg="white")
right_frame.grid(column=1, row=0, sticky="nsew")

# variable pour le mode d'affichage (tree, forum ou radial)
display_mode = tk.StringVar(value='tree')

# configuration du grid pour left_frame
left_frame.rowconfigure(3, weight=1)
left_frame.columnconfigure(0, weight=1)
left_frame.columnconfigure(1, weight=1)

# label pour l'utilisateur connecté
lbl_user = tk.Label(left_frame, text="Non connecté")
lbl_user.grid(column=0, row=0, padx=10, pady=10)

# label pour le mode DB
lbl_db_mode = tk.Label(left_frame, text="db_mode: local")
lbl_db_mode.grid(column=1, row=0, padx=10, pady=10)

# frame pour les boutons
frm_buttons = tk.Frame(left_frame, bg="lightblue")
frm_buttons.grid(column=0, row=1, pady=10)

# frame pour les options d'affichage (boutons radio)
frm_options = tk.Frame(left_frame, bg="lightyellow")
frm_options.grid(column=0, row=2, pady=10)

tk.Label(frm_options, text="Mode d'affichage Mindmap:").pack(anchor='w')
tk.Radiobutton(frm_options, text="Treeview", variable=display_mode, value='tree', command=refresh_mindmap).pack(anchor='w')
tk.Radiobutton(frm_options, text="Forum", variable=display_mode, value='forum', command=refresh_mindmap).pack(anchor='w')
tk.Radiobutton(frm_options, text="Radial", variable=display_mode, value='radial', command=refresh_mindmap).pack(anchor='w')

# frame pour l'affichage des résultats (maps, users, nodes)
frm_result = tk.Frame(left_frame, bg="lightgreen")
frm_result.grid(column=0, row=3, columnspan=2, sticky="nsew", padx=10, pady=10)

# placeholder pour le mindmap dans right_frame
tk.Label(right_frame, text="Zone Mindmap", font=("Arial", 16)).pack(expand=True)

# texte initial dans frm_result
tk.Label(frm_result, text="RESULTS").pack()

# démarrage en mode local et affichage des maps
set_db_mode("local")
display_maps()
root.mainloop()