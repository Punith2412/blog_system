import sqlite3

# Simple SHA256 hash for 'admin123'
password_hash = '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9'

conn = sqlite3.connect('blogdata.db')
cursor = conn.cursor()
cursor.execute('UPDATE users SET password_hash = ? WHERE username = ?', (password_hash, 'admin'))
conn.commit()
conn.close()

print("Password fixed!")
print("Login with: admin / admin123")