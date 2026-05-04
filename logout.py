import utils.session

def logout():
    utils.session.Session.logout()
    return "OK"
