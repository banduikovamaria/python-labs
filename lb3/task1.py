import sqlite3
import os
import hashlib
import secrets

DB_NAME = "users.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                login TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                salt TEXT NOT NULL,
                full_name TEXT NOT NULL
            );
        """)
        conn.commit()


def hash_password(password: str, salt: str) -> str:
    # PBKDF2 (стандартний і безпечніший варіант ніж просто sha256)
    dk = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        120_000
    )
    return dk.hex()


def add_user(login: str, password: str, full_name: str) -> bool:
    salt = secrets.token_hex(16)
    password_hash = hash_password(password, salt)

    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users(login, password, salt, full_name) VALUES (?, ?, ?, ?)",
                (login, password_hash, salt, full_name)
            )
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def update_password(login: str, new_password: str) -> bool:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT login FROM users WHERE login = ?", (login,))
        if cur.fetchone() is None:
            return False

        new_salt = secrets.token_hex(16)
        new_hash = hash_password(new_password, new_salt)

        cur.execute(
            "UPDATE users SET password = ?, salt = ? WHERE login = ?",
            (new_hash, new_salt, login)
        )
        conn.commit()
    return True


def authenticate(login: str, password_input: str) -> bool:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT password, salt FROM users WHERE login = ?", (login,))
        row = cur.fetchone()

    if row is None:
        return False

    stored_hash, salt = row
    check_hash = hash_password(password_input, salt)
    return secrets.compare_digest(stored_hash, check_hash)


def menu():
    print("\n=== Робота з БД (sqlite3) ===")
    print("1. Додати нового користувача")
    print("2. Оновити пароль користувача")
    print("3. Перевірити автентифікацію")
    print("0. Вихід")


def main():
    init_db()

    while True:
        menu()
        choice = input("Оберіть пункт: ").strip()

        if choice == "1":
            login = input("login: ").strip()
            password = input("password: ").strip()
            full_name = input("full_name (ПІБ): ").strip()

            ok = add_user(login, password, full_name)
            print("✅ Користувача додано" if ok else "❌ Такий login вже існує")

        elif choice == "2":
            login = input("login: ").strip()
            new_password = input("new password: ").strip()

            ok = update_password(login, new_password)
            print("✅ Пароль оновлено" if ok else "❌ Користувача не знайдено")

        elif choice == "3":
            login = input("login: ").strip()
            password_input = input("Введіть пароль: ").strip()  # як вимагається в завданні (input)

            ok = authenticate(login, password_input)
            print("✅ Успішна автентифікація" if ok else "❌ Невірний login або пароль")

        elif choice == "0":
            print("Вихід.")
            break
        else:
            print("❌ Невірний пункт меню")


if __name__ == "__main__":
    main()
