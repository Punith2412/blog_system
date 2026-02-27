import sqlite3
import hashlib
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Create database with correct password
def create_db():
    import os
    if os.path.exists('blogdata.db'):
        os.remove('blogdata.db')
    
    conn = sqlite3.connect('blogdata.db')
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password_hash TEXT)''')
    cursor.execute('''CREATE TABLE categories (id INTEGER PRIMARY KEY, name TEXT, slug TEXT, description TEXT, color TEXT)''')
    cursor.execute('''CREATE TABLE posts (id INTEGER PRIMARY KEY, title TEXT, slug TEXT, content TEXT, excerpt TEXT, featured_image TEXT, category_id INTEGER, author_id INTEGER, status TEXT, created_at TIMESTAMP, views INTEGER DEFAULT 0)''')
    
    # CORRECT PASSWORD HASH
    password_hash = '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92'
    cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', ('admin', password_hash))
    
    cursor.execute('INSERT INTO categories (name, slug, description, color) VALUES (?, ?, ?, ?)', 
                  ('Technology', 'technology', 'Tech news', '#3b82f6'))
    
    conn.commit()
    conn.close()
    print("Database created!")

# Login route
@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Verify password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        conn = sqlite3.connect('blogdata.db')
        cursor = conn.cursor()
        stored_hash = cursor.execute('SELECT password_hash FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if stored_hash and password_hash == stored_hash[0]:
            session['user_id'] = 1
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login</title>
        <style>
            body { font-family: Arial; display: flex; justify-content: center; align-items: center; height: 100vh; background: #f4f7f6; }
            .login-card { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); width: 400px; }
            h2 { text-align: center; margin-bottom: 24px; }
            input { width: 100%; padding: 12px; margin-bottom: 16px; border: 2px solid #e2e8f0; border-radius: 8px; box-sizing: border-box; }
            button { width: 100%; padding: 12px; background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; }
            .alert { background: #fee2e2; color: #ef4444; padding: 12px; border-radius: 8px; margin-bottom: 16px; }
        </style>
    </head>
    <body>
        <div class="login-card">
            <h2>Admin Login</h2>
            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    <div class="alert">{{ messages[0] }}</div>
                {% endif %}
            {% endwith %}
            <form method="POST">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Sign In</button>
            </form>
        </div>
    </body>
    </html>
    '''

@app.route('/admin/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard</title>
        <style>
            body { font-family: Arial; margin: 0; background: #f4f7f6; }
            .header { background: white; padding: 20px 40px; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; }
            .content { padding: 40px; }
            .card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
            h1 { margin: 0; }
            .btn { padding: 10px 20px; background: linear-gradient(135deg, #667eea, #764ba2); color: white; text-decoration: none; border-radius: 8px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Dashboard</h1>
            <a href="/admin/logout" class="btn">Logout</a>
        </div>
        <div class="content">
            <div class="card">
                <h2>✅ Login Successful!</h2>
                <p>Welcome to the admin panel, ''' + session.get('username', '') + '''!</p>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/admin/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    create_db()
    print("\n" + "="*50)
    print("Go to: http://127.0.0.1:5000/admin/login")
    print("Username: admin")
    print("Password: admin123")
    print("="*50 + "\n")
    app.run(debug=True)