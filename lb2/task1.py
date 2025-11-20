def analyze_log_file(log_file_path):
    status_counts = {}

    try:
        with open(log_file_path, "r", encoding="utf-8") as file:
            for line in file:
                parts = line.split()

                for i, p in enumerate(parts):
                    # шукаємо частину, яка закінчується на "
                    if p.endswith('"'):
                        # наступна частина — це статус-код
                        if i + 1 < len(parts) and parts[i+1].isdigit():
                            code = parts[i+1]
                            status_counts[code] = status_counts.get(code, 0) + 1
                        break

    except FileNotFoundError:
        print(f"Помилка: файл '{log_file_path}' не знайдено.")
    except IOError:
        print(f"Помилка читання файлу '{log_file_path}'.")

    return status_counts


result = analyze_log_file("apache_logs.txt")
print(result)
