from flask import current_app
from flask_login import UserMixin
from flask_bcrypt import Bcrypt


class User(UserMixin):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.active = True

    def get_username(self):
        return self.username

    @property
    def is_active(self):
        return self.active

    def store_user(self):
        pass


def get_user(user_id):
    user = User(user_id, )


'''
password = current_app.config["PASSWORDS"].get(user_id)
user = User(user_id, password) if password else None
if user is not None:
    user.is_admin = user.username in current_app.config["ADMIN_USERS"]
return user
'''



