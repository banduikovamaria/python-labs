import sqlite3
from datetime import datetime

DB_NAME = "security_events.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    with get_connection() as conn:
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS EventSources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            location TEXT NOT NULL,
            type TEXT NOT NULL
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS EventTypes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type_name TEXT UNIQUE NOT NULL,
            severity TEXT NOT NULL
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS SecurityEvents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            source_id INTEGER NOT NULL,
            event_type_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            ip_address TEXT NULL,
            username TEXT NULL,
            FOREIGN KEY (source_id) REFERENCES EventSources(id),
            FOREIGN KEY (event_type_id) REFERENCES EventTypes(id)
        );
        """)

        conn.commit()
def insert_event_types():
    data = [
        ("Login Success", "Informational"),
        ("Login Failed", "Warning"),
        ("Port Scan Detected", "Warning"),
        ("Malware Alert", "Critical"),
    ]
    with get_connection() as conn:
        conn.executemany(
            "INSERT OR IGNORE INTO EventTypes(type_name, severity) VALUES (?, ?);",
            data
        )
        conn.commit()
def insert_sources():
    data = [
        ("Firewall_A", "10.0.0.1", "Firewall"),
        ("Web_Server_Logs", "10.0.0.20", "Web Server"),
        ("IDS_Sensor_B", "10.0.0.30", "IDS"),
    ]
    with get_connection() as conn:
        conn.executemany(
            "INSERT OR IGNORE INTO EventSources(name, location, type) VALUES (?, ?, ?);",
            data
        )
        conn.commit()
if __name__ == "__main__":
    init_db()
    insert_event_types()
    insert_sources()
    print(" База створена і заповнена базовими даними.")
from datetime import timedelta

def get_id(table, column, value):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT id FROM {table} WHERE {column} = ?", (value,))
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"Не знайдено {value} у таблиці {table}")
        return row[0]


def insert_security_events():
    # беремо id потрібних джерел і типів
    web_source_id = get_id("EventSources", "name", "Web_Server_Logs")
    firewall_source_id = get_id("EventSources", "name", "Firewall_A")
    ids_source_id = get_id("EventSources", "name", "IDS_Sensor_B")

    login_failed_id = get_id("EventTypes", "type_name", "Login Failed")
    login_success_id = get_id("EventTypes", "type_name", "Login Success")
    port_scan_id = get_id("EventTypes", "type_name", "Port Scan Detected")
    malware_id = get_id("EventTypes", "type_name", "Malware Alert")

    now = datetime.now()

    events = [
        # 6 невдалих логінів за останню годину з однієї IP (щоб спрацював запит >5 за 1 год)
        (now - timedelta(minutes=5),  web_source_id, login_failed_id, "Failed login attempt", "203.0.113.10", "admin"),
        (now - timedelta(minutes=10), web_source_id, login_failed_id, "Failed login attempt", "203.0.113.10", "admin"),
        (now - timedelta(minutes=15), web_source_id, login_failed_id, "Failed login attempt", "203.0.113.10", "admin"),
        (now - timedelta(minutes=20), web_source_id, login_failed_id, "Failed login attempt", "203.0.113.10", "admin"),
        (now - timedelta(minutes=25), web_source_id, login_failed_id, "Failed login attempt", "203.0.113.10", "admin"),
        (now - timedelta(minutes=30), web_source_id, login_failed_id, "Failed login attempt", "203.0.113.10", "admin"),

        # інші події за останні 24 години
        (now - timedelta(hours=2), web_source_id, login_success_id, "User logged in successfully", "198.51.100.7", "maria"),
        (now - timedelta(hours=5), web_source_id, login_failed_id, "Wrong password", "198.51.100.7", "maria"),
        (now - timedelta(hours=20), firewall_source_id, port_scan_id, "Port scan detected", "192.0.2.44", None),

        # Critical за останній тиждень
        (now - timedelta(days=2), ids_source_id, malware_id, "Malware signature matched: trojan", "203.0.113.55", None),
        (now - timedelta(days=6), ids_source_id, malware_id, "Suspicious payload: ransomware pattern", "203.0.113.56", None),

        # старіше ніж тиждень (щоб не потрапляло у запит за тиждень)
        (now - timedelta(days=10), ids_source_id, malware_id, "Old critical test event", "203.0.113.57", None),
    ]

    with get_connection() as conn:
        conn.executemany("""
            INSERT INTO SecurityEvents(timestamp, source_id, event_type_id, message, ip_address, username)
            VALUES (?, ?, ?, ?, ?, ?);
        """, [(ts, sid, etid, msg, ip, user) for (ts, sid, etid, msg, ip, user) in events])
        conn.commit()
def register_source(name, location, source_type):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO EventSources(name, location, type) VALUES (?, ?, ?);",
            (name, location, source_type)
        )
        conn.commit()


def register_event_type(type_name, severity):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO EventTypes(type_name, severity) VALUES (?, ?);",
            (type_name, severity)
        )
        conn.commit()


def log_event(source_name, event_type_name, message, ip_address=None, username=None):
    source_id = get_id("EventSources", "name", source_name)
    event_type_id = get_id("EventTypes", "type_name", event_type_name)

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO SecurityEvents(timestamp, source_id, event_type_id, message, ip_address, username)
            VALUES (?, ?, ?, ?, ?, ?);
        """, (datetime.now(), source_id, event_type_id, message, ip_address, username))
        conn.commit()
def query_login_failed_last_24h():
    with get_connection() as conn:
        cur = conn.execute("""
            SELECT se.timestamp, es.name, et.type_name, se.ip_address, se.username, se.message
            FROM SecurityEvents se
            JOIN EventSources es ON se.source_id = es.id
            JOIN EventTypes et ON se.event_type_id = et.id
            WHERE et.type_name = 'Login Failed'
              AND se.timestamp >= datetime('now', '-1 day')
            ORDER BY se.timestamp DESC;
        """)
        return cur.fetchall()


def query_ips_more_than_5_failed_last_1h():
    with get_connection() as conn:
        cur = conn.execute("""
            SELECT se.ip_address, COUNT(*) AS failed_count
            FROM SecurityEvents se
            JOIN EventTypes et ON se.event_type_id = et.id
            WHERE et.type_name = 'Login Failed'
              AND se.timestamp >= datetime('now', '-1 hour')
              AND se.ip_address IS NOT NULL
            GROUP BY se.ip_address
            HAVING COUNT(*) > 5
            ORDER BY failed_count DESC;
        """)
        return cur.fetchall()


def query_critical_last_week_grouped_by_source():
    with get_connection() as conn:
        cur = conn.execute("""
            SELECT es.name AS source, COUNT(*) AS critical_count
            FROM SecurityEvents se
            JOIN EventSources es ON se.source_id = es.id
            JOIN EventTypes et ON se.event_type_id = et.id
            WHERE et.severity = 'Critical'
              AND se.timestamp >= datetime('now', '-7 day')
            GROUP BY es.name
            ORDER BY critical_count DESC;
        """)
        return cur.fetchall()


def query_events_by_keyword(keyword):
    with get_connection() as conn:
        cur = conn.execute("""
            SELECT se.timestamp, es.name, et.type_name, et.severity, se.message
            FROM SecurityEvents se
            JOIN EventSources es ON se.source_id = es.id
            JOIN EventTypes et ON se.event_type_id = et.id
            WHERE se.message LIKE ?
            ORDER BY se.timestamp DESC;
        """, (f"%{keyword}%",))
        return cur.fetchall()
if __name__ == "__main__":
    init_db()
    insert_event_types()
    insert_sources()
    insert_security_events()

    # приклад: додамо ще одну подію через функцію
    log_event("Web_Server_Logs", "Login Failed", "Manual test failed login", "203.0.113.99", "test_user")

    print("✅ База створена і заповнена тестовими даними.\n")

    print("1) Login Failed за 24 години:")
    for row in query_login_failed_last_24h():
        print(row)

    print("\n2) IP з >5 невдалих входів за 1 годину:")
    for row in query_ips_more_than_5_failed_last_1h():
        print(row)

    print("\n3) Critical за тиждень, згруповані за джерелом:")
    for row in query_critical_last_week_grouped_by_source():
        print(row)

    print("\n4) Пошук по keyword='Malware':")
    for row in query_events_by_keyword("Malware"):
        print(row)
