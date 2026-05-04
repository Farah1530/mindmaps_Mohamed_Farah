# cette partie gère le chiffrement du mot de passe
# Farah MOHAMED pour SI-CA1 (projet Python) - 2025-2026
# 29 avril 2026
# encrypt.py : affichage de la fenêtre d'inscription


import bcrypt

password = "Farah".encode('utf-8')

# Génère un sel + hash automatiquement
hashed = bcrypt.hashpw(password, bcrypt.gensalt())

print(hashed)
