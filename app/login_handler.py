from app import login_manager,mongo
# Handles the login and session management of new & existing users


class User:
    def __init__(self,user):
        self.username = user['username']
        self.email = user['email']
        self.password = user['password']
        self.logged_in = False

    def is_authenticated(self):
        return self.logged_in

    def is_active (self):
        return True

    def is_anonymous(self):
        return False
    
    def get_id(self):
        return unicode(self.username)
    
    



@login_manager.user_loader
def load_user(user_id):
    user = User (mongo.db.users.find_one({ 'username' : str(user_id)}))
    return user

