import hashlib
from datetime import datetime

class User:
    def __init__(self, username, password, is_active=True):
        self.username = username
        self.password_hash = self.hash_password(password)
        self.is_active = is_active

    @staticmethod
    def hash_password(password):
        """Хешування пароля через md5"""
        return hashlib.md5(password.encode()).hexdigest()

    def verify_password(self, password):
        """Перевірка правильності пароля"""
        return self.password_hash == hashlib.md5(password.encode()).hexdigest()

    def __repr__(self):
        return f"<User: {self.username}, active={self.is_active}>"



class Administrator(User):
    def __init__(self, username, password, permissions=None):
        super().__init__(username, password, is_active=True)
        self.permissions = permissions if permissions else []

    def add_permission(self, perm):
        self.permissions.append(perm)


class RegularUser(User):
    def __init__(self, username, password):
        super().__init__(username, password, is_active=True)
        self.last_login = None

    def update_last_login(self):
        self.last_login = datetime.now()


class GuestUser(User):
    def __init__(self, username):
        super().__init__(username, password="", is_active=False)
        self.access_level = "read-only"



class AccessControl:
    def __init__(self):
        self.users = {}  # ключ = юзернейм, значення = об'єкт User

    def add_user(self, user):
        self.users[user.username] = user

    def authenticate_user(self, username, password):
        user = self.users.get(username)

        if user and user.is_active and user.verify_password(password):
            if isinstance(user, RegularUser):
                user.update_last_login()
            return user

        return None



if __name__ == "__main__":
    access = AccessControl()

    admin = Administrator("admin", "1234", permissions=["edit_users"])
    user1 = RegularUser("maria", "pass123")
    guest = GuestUser("visitor")

    access.add_user(admin)
    access.add_user(user1)
    access.add_user(guest)

    print("=== Спроба входу ===")
    username = input("Введіть імʼя користувача: ")
    password = input("Введіть пароль: ")

    authenticated = access.authenticate_user(username, password)

    if authenticated:
        print("Успішний вхід:", authenticated)
        if isinstance(authenticated, RegularUser):
            print("Останній вхід:", authenticated.last_login)
    else:
        print("Помилка автентифікації.")
