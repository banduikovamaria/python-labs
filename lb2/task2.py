import hashlib

def generate_file_hashes(*file_paths):
    hashes = {}

    for path in file_paths:
        try:
            with open(path, "rb") as file:
                data = file.read()
                file_hash = hashlib.sha256(data).hexdigest()
                hashes[path] = file_hash

        except FileNotFoundError:
            print(f"Помилка: файл '{path}' не знайдено.")
        except IOError:
            print(f"Помилка читання файлу '{path}'.")

    return hashes

print(generate_file_hashes("apache_logs.txt", "task2.py"))
