import sqlite3
import hashlib
from datetime import datetime

def get_db_connection():
    conn = sqlite3.connect('blogdata.db')
    conn.row_factory = sqlite3.Row
    return conn

def row_to_dict(row):
    return dict(row) if row else None

# ==================== USER FUNCTIONS ====================

def get_user_by_username(username):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return row_to_dict(user)

def get_user_by_id(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return row_to_dict(user)

def verify_password(username, password):
    user = get_user_by_username(username)
    if user:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return user['password_hash'] == password_hash
    return False

# ==================== POST FUNCTIONS ====================

def get_all_posts(status=None):
    conn = get_db_connection()
    query = '''
        SELECT p.*, c.name as category_name, u.username as author_name
        FROM posts p
        LEFT JOIN categories c ON p.category_id = c.id
        LEFT JOIN users u ON p.author_id = u.id
    '''
    if status and status != 'all':
        query += ' WHERE p.status = ?'
        query += ' ORDER BY p.created_at DESC'
        posts = conn.execute(query, (status,)).fetchall()
    else:
        query += ' ORDER BY p.created_at DESC'
        posts = conn.execute(query).fetchall()
    conn.close()
    return [row_to_dict(p) for p in posts]

def get_post_by_id(post_id):
    conn = get_db_connection()
    post = conn.execute('''
        SELECT p.*, c.name as category_name, u.username as author_name
        FROM posts p
        LEFT JOIN categories c ON p.category_id = c.id
        LEFT JOIN users u ON p.author_id = u.id
        WHERE p.id = ?
    ''', (post_id,)).fetchone()
    conn.close()
    return row_to_dict(post)

def get_post_by_slug(slug):
    conn = get_db_connection()
    post = conn.execute('''
        SELECT p.*, c.name as category_name, c.slug as category_slug, u.username as author_name, u.bio as author_bio
        FROM posts p
        LEFT JOIN categories c ON p.category_id = c.id
        LEFT JOIN users u ON p.author_id = u.id
        WHERE p.slug = ?
    ''', (slug,)).fetchone()
    conn.close()
    return row_to_dict(post)

def get_posts_by_category(category_id):
    conn = get_db_connection()
    posts = conn.execute('''
        SELECT p.*, c.name as category_name, u.username as author_name
        FROM posts p
        LEFT JOIN categories c ON p.category_id = c.id
        LEFT JOIN users u ON p.author_id = u.id
        WHERE p.category_id = ? AND p.status = 'published'
        ORDER BY p.created_at DESC
    ''', (category_id,)).fetchall()
    conn.close()
    return [row_to_dict(p) for p in posts]

def search_posts(query):
    conn = get_db_connection()
    posts = conn.execute('''
        SELECT p.*, c.name as category_name, u.username as author_name
        FROM posts p
        LEFT JOIN categories c ON p.category_id = c.id
        LEFT JOIN users u ON p.author_id = u.id
        WHERE (p.title LIKE ? OR p.content LIKE ?) AND p.status = 'published'
        ORDER BY p.created_at DESC
    ''', (f'%{query}%', f'%{query}%')).fetchall()
    conn.close()
    return [row_to_dict(p) for p in posts]

def create_post(title, content, category_id, author_id, excerpt='', featured_image='', status='published'):
    conn = get_db_connection()
    cursor = conn.cursor()
    slug = title.lower().replace(' ', '-').replace('_', '-')
    cursor.execute('''
        INSERT INTO posts (title, slug, content, excerpt, category_id, author_id, featured_image, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, slug, content, excerpt, category_id, author_id, featured_image, status))
    conn.commit()
    post_id = cursor.lastrowid
    conn.close()
    return post_id

def update_post(post_id, title, content, category_id, excerpt='', featured_image='', status='published'):
    conn = get_db_connection()
    slug = title.lower().replace(' ', '-').replace('_', '-')
    conn.execute('''
        UPDATE posts 
        SET title = ?, slug = ?, content = ?, excerpt = ?, category_id = ?, featured_image = ?, status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (title, slug, content, excerpt, category_id, featured_image, status, post_id))
    conn.commit()
    conn.close()

def delete_post(post_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    conn.commit()
    conn.close()

def get_drafts():
    conn = get_db_connection()
    posts = conn.execute('''
        SELECT p.*, c.name as category_name, u.username as author_name
        FROM posts p
        LEFT JOIN categories c ON p.category_id = c.id
        LEFT JOIN users u ON p.author_id = u.id
        WHERE p.status = 'draft'
        ORDER BY p.created_at DESC
    ''').fetchall()
    conn.close()
    return [row_to_dict(p) for p in posts]

def get_scheduled_posts():
    conn = get_db_connection()
    posts = conn.execute('''
        SELECT p.*, c.name as category_name, u.username as author_name
        FROM posts p
        LEFT JOIN categories c ON p.category_id = c.id
        LEFT JOIN users u ON p.author_id = u.id
        WHERE p.status = 'scheduled'
        ORDER BY p.created_at DESC
    ''').fetchall()
    conn.close()
    return [row_to_dict(p) for p in posts]

# ==================== CATEGORY FUNCTIONS ====================

def get_all_categories():
    conn = get_db_connection()
    categories = conn.execute('SELECT * FROM categories ORDER BY name').fetchall()
    conn.close()
    return [row_to_dict(c) for c in categories]

def get_category_by_slug(slug):
    conn = get_db_connection()
    category = conn.execute('SELECT * FROM categories WHERE slug = ?', (slug,)).fetchone()
    conn.close()
    return row_to_dict(category)

def get_category_by_id(category_id):
    conn = get_db_connection()
    category = conn.execute('SELECT * FROM categories WHERE id = ?', (category_id,)).fetchone()
    conn.close()
    return row_to_dict(category)

def create_category(name, description='', color='#6366f1'):
    conn = get_db_connection()
    slug = name.lower().replace(' ', '-').replace('_', '-')
    try:
        conn.execute('INSERT INTO categories (name, slug, description, color) VALUES (?, ?, ?, ?)',
                    (name, slug, description, color))
        conn.commit()
        result = True
    except:
        result = False
    conn.close()
    return result

# ==================== COMMENT FUNCTIONS ====================

def get_comments_by_post(post_id):
    conn = get_db_connection()
    comments = conn.execute('''
        SELECT c.*, u.username as user_username
        FROM comments c
        LEFT JOIN users u ON c.user_id = u.id
        WHERE c.post_id = ? AND c.status = 'approved'
        ORDER BY c.created_at DESC
    ''', (post_id,)).fetchall()
    conn.close()
    return [row_to_dict(c) for c in comments]

def add_comment(post_id, content, author_name='Anonymous', user_id=None):
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO comments (post_id, user_id, author_name, content, status)
        VALUES (?, ?, ?, ?, 'approved')
    ''', (post_id, user_id, author_name, content))
    conn.commit()
    conn.close()

# ==================== SUBSCRIBER FUNCTIONS ====================

def add_subscriber(email):
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO subscribers (email) VALUES (?)', (email,))
        conn.commit()
        result = True
    except:
        result = False
    conn.close()
    return result

def get_subscriber_count():
    conn = get_db_connection()
    count = conn.execute('SELECT COUNT(*) FROM subscribers WHERE status = "active"').fetchone()[0]
    conn.close()
    return count

# ==================== ANALYTICS FUNCTIONS ====================

def track_visit(post_id, ip, user_agent, referrer):
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO analytics (post_id, visitor_ip, user_agent, referrer)
        VALUES (?, ?, ?, ?)
    ''', (post_id, ip, user_agent, referrer))
    conn.commit()
    conn.close()

def increment_post_views(post_id):
    conn = get_db_connection()
    conn.execute('UPDATE posts SET views = views + 1 WHERE id = ?', (post_id,))
    conn.commit()
    conn.close()

def get_popular_posts(limit=5):
    conn = get_db_connection()
    posts = conn.execute('''
        SELECT p.*, c.name as category_name, u.username as author_name
        FROM posts p
        LEFT JOIN categories c ON p.category_id = c.id
        LEFT JOIN users u ON p.author_id = u.id
        WHERE p.status = 'published'
        ORDER BY p.views DESC
        LIMIT ?
    ''', (limit,)).fetchall()
    conn.close()
    return [row_to_dict(p) for p in posts]

def get_analytics_summary():
    conn = get_db_connection()
    total_visits = conn.execute('SELECT COUNT(*) FROM analytics').fetchone()[0]
    total_posts = conn.execute('SELECT COUNT(*) FROM posts WHERE status = "published"').fetchone()[0]
    total_subscribers = conn.execute('SELECT COUNT(*) FROM subscribers WHERE status = "active"').fetchone()[0]
    conn.close()
    return {
        'total_visits': total_visits,
        'total_posts': total_posts,
        'total_subscribers': total_subscribers
    }

# ==================== AI CONTEXT FUNCTIONS ====================

def get_all_posts_for_ai():
    conn = get_db_connection()
    posts = conn.execute('''
        SELECT p.id, p.title, p.slug, p.content, p.excerpt, p.views,
               c.name as category_name, u.username as author_name
        FROM posts p
        LEFT JOIN categories c ON p.category_id = c.id
        LEFT JOIN users u ON p.author_id = u.id
        WHERE p.status = 'published'
        ORDER BY p.created_at DESC
    ''').fetchall()
    conn.close()
    return [row_to_dict(p) for p in posts]

def format_posts_for_context(posts):
    if not posts:
        return "No posts available yet."
    context = "BLOG POSTS:\n\n"
    for i, post in enumerate(posts, 1):
        context += f"""POST {i}:
Title: {post['title']}
Author: {post['author_name']}
Category: {post['category_name']}
Content: {post['content']}

"""
    return context