import sqlite3
import os

db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database', 'healthpredict.db'))

print(f"Database File: {db_path}")
print(f"File Exists: {os.path.exists(db_path)} ({os.path.getsize(db_path)} bytes)")

conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
tables = [row[0] for row in cur.fetchall()]
print(f"\nTables Found: {tables}")

for table in tables:
    print(f"\n================ Schema: {table} ================")
    cur.execute(f"PRAGMA table_info({table});")
    cols = cur.fetchall()
    for col in cols:
        cid, name, col_type, notnull, dflt_value, pk = col
        pk_str = " [PRIMARY KEY]" if pk else ""
        nn_str = " NOT NULL" if notnull else ""
        print(f"  - {name:18} {col_type:10}{nn_str}{pk_str}")

conn.close()
