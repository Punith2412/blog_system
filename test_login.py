import sqlite3
import hashlib

# Test if we can create user and verify password
password = 'admin123'
password_hash = hashlib.sha256(password.encode()).hexdigest()

print(f"Password: {password}")
print(f"Hash: {password_hash}")

# Create database
conn = sqlite3.connect('test_blog.db')
cursor = conn.cursor()

# Create users table
cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )
''')

# Insert user
cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', 
              ('admin', password_hash))
conn.commit()

# Verify
stored_hash = cursor.execute('SELECT password_hash FROM users WHERE username = ?', 
                             ('admin',)).fetchone()[0]

print(f"Stored hash: {stored_hash}")
print(f"Match: {password_hash == stored_hash}")

conn.close()

if password_hash == stored_hash:
    print("\n✅ LOGIN WILL WORK!")
else:
    print("\n❌ PROBLEM!")