def filter_ips(input_file_path, output_file_path, allowed_ips):
    ip_counts = {ip: 0 for ip in allowed_ips}

    try:
        with open(input_file_path, "r", encoding="utf-8") as infile:
            for line in infile:
                parts = line.split()
                if not parts:
                    continue

                ip = parts[0]

                if ip in ip_counts:
                    ip_counts[ip] += 1

        with open(output_file_path, "w", encoding="utf-8") as outfile:
            for ip, count in ip_counts.items():
                outfile.write(f"{ip} - {count}\n")

    except FileNotFoundError:
        print(f"Помилка: файл '{input_file_path}' не знайдено.")
    except IOError:
        print("Помилка при записі у файл.")

    return ip_counts
allowed = ["83.149.9.216", "93.114.45.13"]

result = filter_ips("apache_logs.txt", "filtered_result.txt", allowed)
print(result)


