from flask import Flask, render_template, request, redirect, url_for, flash, session, abort, jsonify
from functools import wraps
import markdown
import bleach
from datetime import datetime
import os
import sqlite3

from init_db import init_db
init_db()

from models import (
    get_all_posts, get_post_by_id, get_post_by_slug, get_posts_by_category,
    create_post, update_post, delete_post, search_posts,
    get_all_categories, get_category_by_slug, create_category,
    get_user_by_username, verify_password,
    add_comment, get_comments_by_post,
    add_subscriber, get_subscriber_count,
    track_visit, get_analytics_summary, get_popular_posts,
    increment_post_views, get_drafts, get_scheduled_posts,
    get_all_posts_for_ai, format_posts_for_context
)

import ai_service
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "blogdata.db")

@app.template_filter('markdown')
def render_markdown(text):
    if text:
        return markdown.markdown(text, extensions=['fenced_code', 'tables'])
    return ''

@app.template_filter('truncate_words')
def truncate_words(text, length=20):
    if not text:
        return ''
    words = str(text).split()
    return ' '.join(words[:length]) + '...' if len(words) > length else text

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('admin_login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# ---------------- PUBLIC ROUTES ----------------

@app.route('/')
def home():
    posts = get_all_posts(status='published')
    categories = get_all_categories()
    popular_posts = get_popular_posts(3)
    subscriber_count = get_subscriber_count()
    featured_post = posts[0] if posts else None
    recent_posts = posts[1:10] if posts else []
    return render_template(
        'home.html',
        featured_post=featured_post,
        recent_posts=recent_posts,
        categories=categories,
        popular_posts=popular_posts,
        subscriber_count=subscriber_count,
        now=datetime.now()
    )

@app.route('/post/<slug>')
def post(slug):
    post = get_post_by_slug(slug)
    if not post:
        abort(404)
    increment_post_views(post['id'])
    track_visit(post_id=post['id'], ip=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                referrer=request.referrer)
    comments = get_comments_by_post(post['id'])
    categories = get_all_categories()
    popular_posts = get_popular_posts(3)
    return render_template('post.html', post=post,
                           comments=comments,
                           categories=categories,
                           popular_posts=popular_posts)

@app.route('/author/<username>')
def author_profile(username):
    user = get_user_by_username(username)
    if not user:
        abort(404)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    posts = conn.execute(
        '''SELECT p.*, c.name as category_name
           FROM posts p
           LEFT JOIN categories c ON p.category_id = c.id
           WHERE p.author_id = ? AND p.status = "published"
           ORDER BY p.created_at DESC''',
        (user['id'],)
    ).fetchall()
    conn.close()

    categories = get_all_categories()
    popular_posts = get_popular_posts(3)
    return render_template('author.html',
                           author=user,
                           posts=posts,
                           categories=categories,
                           popular_posts=popular_posts)

# (rest of your routes remain SAME — no changes needed)

@app.route('/simple')
def simple():
    return render_template('simple_test.html')

if __name__ == "__main__":
    app.run()