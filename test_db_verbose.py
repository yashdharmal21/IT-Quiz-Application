# test_db_verbose.py
import mysql.connector
from mysql.connector import Error
import traceback

HOST = "172.20.10.3"
USER = "root"
PASSWORD = ""   # empty password for your XAMPP root
DATABASE = "quiz_event"

print("Running DB connectivity test...")
try:
    conn = mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=DATABASE,
        connection_timeout=5
    )
    print("Attempted to connect to:", HOST)
    if conn.is_connected():
        print("SUCCESS: Connected to MySQL server.")
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION();")
        ver = cursor.fetchone()
        print("MySQL Server version:", ver)
        # list databases and show quiz_event existence
        cursor.execute("SHOW DATABASES;")
        dbs = [d[0] for d in cursor.fetchall()]
        print("Databases visible:", dbs)
        if DATABASE in dbs:
            print(f"Database '{DATABASE}' exists.")
            cursor.execute(f"SHOW TABLES IN {DATABASE};")
            tables = [t[0] for t in cursor.fetchall()]
            print(f"Tables in {DATABASE}:", tables)
        else:
            print(f"Database '{DATABASE}' does NOT exist.")
        cursor.close()
    else:
        print("Connected but conn.is_connected() returned False")
except Error as e:
    print("MYSQL ERROR:", e)
    traceback.print_exc()
except Exception as e:
    print("GENERAL ERROR:", e)
    traceback.print_exc()
finally:
    try:
        if 'conn' in locals() and conn.is_connected():
            conn.close()
            print("Connection closed.")
    except Exception:
        pass
