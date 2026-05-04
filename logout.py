# cette partie gère la déconnexion
# Farah MOHAMED pour SI-CA1 (projet Python) - 2025-2026
# 29 avril 2026
# logout.py : affichage de la fenêtre de déconnexion

import utils.session

def logout():
    utils.session.Session.logout()
    return "OK"
