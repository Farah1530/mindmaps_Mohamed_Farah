# Projet mindmaps : prototype d'affichage de mindmap en radial et forum 
# Farah MOHAMED SI-CA1 (projet Python) - 2025-2026
# 13 avril 2026
# model.py : définition des fonctions pour interagir avec la base de données

import mysql.connector
import bcrypt
from utils.config import get_db_config


# Fonction pour obtenir une connexion à la base de données
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


# renvoie la liste des maps (sans les nodes) pour l'affichage de la page d'accueil
def get_maps(db_mode):
    return fetch_all("select id, title, author_id from maps", None, db_mode)


def get_users(db_mode):
    return fetch_all("select id, pseudo, color from users", None, db_mode)

def get_nodes(db_mode):
    return fetch_all("select id, parent_id, author_id, text, level from nodes", None, db_mode)

def get_nodes( db_mode):
    return fetch_all("select id, parent_id, author_id, text, level from nodes ", None, db_mode)


# renvoie la liste de tous les nodes d'un map (avec le pseudo de l'auteur et sa couleur)
def get_nodes_for_map(map_id, db_mode):
    return fetch_all("select nodes.id, parent_id, author_id, text, nodes.level,users.color " \
    "from nodes inner join users on nodes.author_id = users.id " \
    "where map_id=%s", (map_id,), db_mode)

# fonctions pour insérer, mettre à jour et supprimer des maps et des nodes
# fonction pour insérer un node (retourne l'id du node créé)

# fonction pour vérifier les identifiants de connexion d'un utilisateur (retourne les infos de l'utilisateur si ok, sinon None)
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
    # Vérifier le mot de passe avec bcrypt
    if bcrypt.checkpw(password.encode(), stored):
        return row
    return None

def check_register(pseudo,password, db_mode="local"):
    db = get_connection(db_mode)
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id FROM users WHERE pseudo=%s", (pseudo,))
    row = cursor.fetchone()
    db.close()
    if row:
        return None  # L'utilisateur existe déjà
    # Si l'utilisateur n'existe pas, on peut l'enregistrer
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    db = get_connection(db_mode)
    cursor = db.cursor()
    cursor.execute("INSERT INTO users (pseudo, hash) VALUES (%s, %s)", (pseudo, hashed))
    db.commit()
    db.close()
    return "OK"          


#fonction pour vérifier les inscriptions
def check_registration(pseudo, password, db_mode="local"):
    db = get_connection(db_mode)
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id FROM users WHERE pseudo=%s", (pseudo,))
    row = cursor.fetchone()
    db.close()
    if row:
        return None  # L'utilisateur existe déjà
    # Si l'utilisateur n'existe pas, on peut l'enregistrer
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    db = get_connection(db_mode)
    cursor = db.cursor()
    cursor.execute("INSERT INTO users (pseudo, hash) VALUES (%s, %s)", (pseudo, hashed))
    db.commit()
    db.close()

    return {"id": cursor.lastrowid, "pseudo": pseudo}


def update_node_text(node_id, new_text, db_mode="local"):
    db = get_connection(db_mode)
    cursor = db.cursor()
    cursor.execute("UPDATE nodes SET text=%s WHERE id=%s", (new_text, node_id))
    db.commit()
    db.close()

def delete_node(node_id, db_mode="local"):
    db = get_connection(db_mode)
    cursor = db.cursor()
    cursor.execute("DELETE FROM nodes WHERE id=%s", (node_id,))
    db.commit()
    db.close()

def insert_node(map_id, parent_id, author_id, text, level, db_mode="local"):
    db = get_connection(db_mode)
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO nodes (map_id, parent_id, author_id, text, level) VALUES (%s, %s, %s, %s, %s)",
        (map_id, parent_id, author_id, text, level)
    )
    db.commit()
    db.close()

# je vais crée une nouvelle map
# Créer une nouvelle map
def insert_map(title, author_id, db_mode="local"):
    db = get_connection(db_mode) #on se connecte à la DB
    cursor = db.cursor()# on prepare l outil pour envoyer du sql grace a cursor
    cursor.execute(
        "INSERT INTO maps (title, author_id) VALUES (%s, %s)",
        (title, author_id)
    )   #et avc cursor.excute pour inserer les donnée que y a dans ()
    db.commit()# sert a confirmer sans sa la sauvegarde ne se fait pas
    new_id = cursor.lastrowid  # et la on recupere l id que my sql nous a donnée automatiquement 
    db.close()  # et la on ferme la connexion 
    return new_id #on reprend l id crée si on le veut directement


# Renommer une map existante
def update_map_title(map_id, new_title, db_mode="local"):
    db = get_connection(db_mode) #connection a la db
    cursor = db.cursor() #comme avant on prepare l outils 
    cursor.execute(
        "UPDATE maps SET title=%s WHERE id=%s",
        (new_title, map_id)
    ) # et on excute la commande uniquement pour cette id 
    db.commit() #on confirme les modif
    db.close() # on ferme 


# Supprimer une map et tous ses nœuds
# On supprime d'abord les nodes, sinon MySQL refuse (clé étrangère)
def delete_map(map_id, db_mode="local"):
    db = get_connection(db_mode) #connection avec la db
    cursor = db.cursor() #prepare l outil   
    cursor.execute("DELETE FROM nodes WHERE map_id=%s", (map_id,))  # 1. nodes d'abord parce que dans la BD les nodes ont un map_id donc MYSQL refuse d abord les node apres la map
    cursor.execute("DELETE FROM maps WHERE id=%s", (map_id,))       # 2. puis la map
    db.commit() #confirme les 2 suppression
    db.close() #et on ferme
