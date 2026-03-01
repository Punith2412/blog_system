import sqlite3

conn = sqlite3.connect("blogdata.db")
cur = conn.cursor()

tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()

print("Tables in database:")
for t in tables:
    print("-", t[0])

conn.close()