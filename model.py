# Projet mindmaps : prototype d'affichage de mindmap en radial et forum 
# Farah MOHAMED SI-CA1 (projet Python) - 2025-2026
# 13 avril 2026
# model.py : définition des fonctions pour interagir avec la base de données

import mysql.connector
import bcrypt
from utils.config import get_db_config


# fonction pour obtenir une connexion à la base de données
def get_connection(db_mode="local"):
    cfg = get_db_config(db_mode)
    return mysql.connector.connect(
        host=cfg["host"],
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        port=cfg["port"]
    )

# renvoie le résultat d'une requête SQL en mode dictionnaire
def fetch_all(sql_query, params=None, db_mode="local"):
    db = get_connection(db_mode)
    cursor = db.cursor(dictionary=True)
    if params:
        cursor.execute(sql_query, params)
    else:
        cursor.execute(sql_query)
    rows = cursor.fetchall()
    db.close()
    return rows


# renvoie la liste des maps pour l'affichage dans le treeview de gauche
def get_maps(db_mode):
    return fetch_all("select id, title, author_id from maps", None, db_mode)


# renvoie la liste des users (sans le hash pour la sécurité)
def get_users(db_mode):
    return fetch_all("select id, pseudo, color from users", None, db_mode)

# renvoie la liste de tous les nodes
def get_nodes(db_mode):
    return fetch_all("select id, parent_id, author_id, text, level from nodes", None, db_mode)


# renvoie la liste de tous les nodes d'un map (avec le pseudo de l'auteur et sa couleur)
def get_nodes_for_map(map_id, db_mode):
    return fetch_all("select nodes.id, parent_id, author_id, text, nodes.level, users.color " \
    "from nodes inner join users on nodes.author_id = users.id " \
    "where map_id=%s", (map_id,), db_mode)

# vérifie les identifiants de connexion (retourne les infos user si ok, sinon None)
def check_login(pseudo, password, db_mode="local"):
    db = get_connection(db_mode)
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, pseudo, hash, level FROM users WHERE pseudo=%s", (pseudo,))
    row = cursor.fetchone()
    db.close()
    if not row:
        return None
    stored = row["hash"]
    if isinstance(stored, str):
        stored = stored.encode()
    # vérifier le mot de passe avec bcrypt
    if bcrypt.checkpw(password.encode(), stored):
        return row
    return None

# vérifie et effectue l'inscription d'un nouvel utilisateur
# on passe maintenant la couleur en paramètre (ajout étape 6)
def check_register(pseudo, password, color="white", db_mode="local"):
    db = get_connection(db_mode)
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id FROM users WHERE pseudo=%s", (pseudo,))
    row = cursor.fetchone()
    db.close()
    if row:
        return "EXISTS"  # le pseudo est déjà pris
    # le pseudo est libre, on hashe le mot de passe et on insère avec la couleur
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    db = get_connection(db_mode)
    cursor = db.cursor()
    cursor.execute("INSERT INTO users (pseudo, hash, color) VALUES (%s, %s, %s)", (pseudo, hashed, color))
    db.commit()
    db.close()
    return "OK"

# modifier le texte d'un node existant
def update_node_text(node_id, new_text, db_mode="local"):
    db = get_connection(db_mode)
    cursor = db.cursor()
    cursor.execute("UPDATE nodes SET text=%s WHERE id=%s", (new_text, node_id))
    db.commit()
    db.close()

# supprimer un node (les enfants sont supprimés en cascade grâce à la BD)
def delete_node(node_id, db_mode="local"):
    db = get_connection(db_mode)
    cursor = db.cursor()
    cursor.execute("DELETE FROM nodes WHERE id=%s", (node_id,))
    db.commit()
    db.close()

# insérer un nouveau node dans un map
def insert_node(map_id, parent_id, author_id, text, level, db_mode="local"):
    db = get_connection(db_mode)
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO nodes (map_id, parent_id, author_id, text, level) VALUES (%s, %s, %s, %s, %s)",
        (map_id, parent_id, author_id, text, level)
    )
    db.commit()
    db.close()



# ETAPE 6 — CRUD sur les maps


# créer une nouvelle map
# on reçoit le titre et l'id de l'auteur (l'utilisateur connecté)
# on retourne l'id de la map créée (utile pour créer le nœud racine juste après)
def insert_map(title, author_id, db_mode="local"):
    db = get_connection(db_mode)
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO maps (title, author_id) VALUES (%s, %s)",
        (title, author_id)
    )
    db.commit()
    new_id = cursor.lastrowid  # récupère l'id auto-généré par MySQL
    db.close()
    return new_id


# renommer une map existante
# on reçoit l'id de la map et le nouveau titre
def update_map_title(map_id, new_title, db_mode="local"):
    db = get_connection(db_mode)
    cursor = db.cursor()
    cursor.execute(
        "UPDATE maps SET title=%s WHERE id=%s",
        (new_title, map_id)
    )
    db.commit()
    db.close()


# supprimer une map et tous ses nœuds
# IMPORTANT : on supprime d'abord les nodes de la map,
# sinon MySQL refuse à cause de la contrainte de clé étrangère
def delete_map(map_id, db_mode="local"):
    db = get_connection(db_mode)
    cursor = db.cursor()
    cursor.execute("DELETE FROM nodes WHERE map_id=%s", (map_id,))  # 1. supprimer les nodes
    cursor.execute("DELETE FROM maps WHERE id=%s", (map_id,))       # 2. supprimer la map
    db.commit()
    db.close()