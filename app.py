from flask import Flask, render_template, request, redirect, url_for, flash, session, abort, jsonify
from functools import wraps
import markdown
import bleach
from datetime import datetime
import os
import sqlite3

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

@app.template_filter('markdown')
def render_markdown(text):
    if text:
        html = markdown.markdown(text, extensions=['fenced_code', 'tables'])
        return html
    return ''

@app.template_filter('truncate_words')
def truncate_words(text, length=20):
    if not text:
        return ''
    words = str(text).split()
    if len(words) > length:
        return ' '.join(words[:length]) + '...'
    return text

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('admin_login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# ==================== PUBLIC ROUTES ====================

@app.route('/')
def home():
    posts = get_all_posts(status='published')
    categories = get_all_categories()
    popular_posts = get_popular_posts(3)
    subscriber_count = get_subscriber_count()
    featured_post = posts[0] if posts else None
    recent_posts = posts[1:10] if posts else []
    return render_template('home.html', featured_post=featured_post, recent_posts=recent_posts,
                         categories=categories, popular_posts=popular_posts, subscriber_count=subscriber_count, now=datetime.now())

@app.route('/post/<slug>')
def post(slug):
    post = get_post_by_slug(slug)
    if not post:
        abort(404)
    increment_post_views(post['id'])
    track_visit(post_id=post['id'], ip=request.remote_addr, user_agent=request.headers.get('User-Agent'), referrer=request.referrer)
    comments = get_comments_by_post(post['id'])
    categories = get_all_categories()
    popular_posts = get_popular_posts(3)
    return render_template('post.html', post=post, comments=comments, categories=categories, popular_posts=popular_posts)

@app.route('/category/<slug>')
def category(slug):
    category = get_category_by_slug(slug)
    if not category:
        abort(404)
    posts = get_posts_by_category(category['id'])
    categories = get_all_categories()
    popular_posts = get_popular_posts(3)
    return render_template('category.html', category=category, posts=posts, categories=categories, popular_posts=popular_posts)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return redirect(url_for('home'))
    posts = search_posts(query)
    categories = get_all_categories()
    popular_posts = get_popular_posts(3)
    return render_template('search.html', query=query, posts=posts, categories=categories, popular_posts=popular_posts)

@app.route('/ai-search')
def ai_search():
    query = request.args.get('q', '').strip().lower()
    if not query:
        return redirect(url_for('home'))
    all_posts = get_all_posts(status='published')
    results = []
    for post in all_posts:
        score = 0
        title_lower = post['title'].lower()
        content_lower = post['content'].lower()
        if query in title_lower:
            score += 100
        if query in content_lower:
            score += 50
        if score > 0:
            post['relevance_score'] = score
            results.append(post)
    results.sort(key=lambda x: x['relevance_score'], reverse=True)
    categories = get_all_categories()
    popular_posts = get_popular_posts(3)
    return render_template('ai_search.html', query=query, posts=results, categories=categories, popular_posts=popular_posts, total_results=len(results))

@app.route('/recommended-for-you')
def recommended_posts():
    all_posts = get_all_posts(status='published')
    categories = get_all_categories()
    popular_posts = get_popular_posts(3)
    recommended = []
    for post in all_posts:
        score = min(post['views'] / 10, 20)
        post['recommendation_score'] = score
        recommended.append(post)
    recommended.sort(key=lambda x: x.get('recommendation_score', 0), reverse=True)
    recommended = recommended[:6]
    return render_template('recommended.html', posts=recommended, categories=categories, popular_posts=popular_posts, recommendation_type="Recommended For You")

@app.route('/about')
def about():
    categories = get_all_categories()
    return render_template('about.html', categories=categories)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    categories = get_all_categories()
    if request.method == 'POST':
        flash('Thank you for your message! We will get back to you soon.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html', categories=categories)

@app.route('/newsletter/subscribe', methods=['POST'])
def newsletter_subscribe():
    email = request.form.get('email')
    if email:
        if add_subscriber(email):
            flash('Successfully subscribed!', 'success')
        else:
            flash('Already subscribed.', 'info')
    return redirect(url_for('newsletter_success'))

@app.route('/newsletter/success')
def newsletter_success():
    categories = get_all_categories()
    return render_template('newsletter_success.html', categories=categories)

@app.route('/newsletter/unsubscribe', methods=['GET', 'POST'])
def newsletter_unsubscribe():
    categories = get_all_categories()
    if request.method == 'POST':
        flash('You have been unsubscribed from our newsletter.', 'success')
        return redirect(url_for('home'))
    return render_template('newsletter_unsubscribe.html', categories=categories)

@app.route('/comment/<int:post_id>', methods=['POST'])
def add_comment_route(post_id):
    content = request.form.get('content')
    author_name = request.form.get('author_name') or 'Anonymous'
    if content:
        add_comment(post_id, content, author_name=author_name)
        flash('Comment added successfully!', 'success')
    post = get_post_by_id(post_id)
    return redirect(url_for('post', slug=post['slug']))

@app.route('/author/<username>')
def author_profile(username):
    user = get_user_by_username(username)
    if not user:
        abort(404)
    conn = sqlite3.connect('blogdata.db')
    conn.row_factory = sqlite3.Row
    posts = conn.execute('SELECT p.*, c.name as category_name FROM posts p LEFT JOIN categories c ON p.category_id = c.id WHERE p.author_id = ? AND p.status = "published" ORDER BY p.created_at DESC', (user['id'],)).fetchall()
    conn.close()
    categories = get_all_categories()
    popular_posts = get_popular_posts(3)
    return render_template('author.html', author=user, posts=posts, categories=categories, popular_posts=popular_posts)

# ==================== AI CHAT ROUTES ====================

@app.route('/ai')
def ai_page():
    posts = get_all_posts(status='published')
    categories = get_all_categories()
    return render_template('ai_chatbot.html', posts=posts, categories=categories)

@app.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        if not user_message:
            return jsonify({'response': 'Please enter a message.'})
        posts = get_all_posts_for_ai()
        blog_context = format_posts_for_context(posts)
        response = ai_service.get_ai_response(user_message, blog_context)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'response': f'Error: {str(e)}'})

# ==================== ADMIN ROUTES ====================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    categories = get_all_categories()
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if verify_password(username, password):
            user = get_user_by_username(username)
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('admin_panel'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('admin_login.html', categories=categories)

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/admin')
@admin_required
def admin_panel():
    posts = get_all_posts(status='all')
    drafts = get_drafts()
    scheduled = get_scheduled_posts()
    analytics = get_analytics_summary()
    categories = get_all_categories()
    total_posts = len([p for p in posts if p['status'] == 'published'])
    total_drafts = len(drafts)
    total_scheduled = len(scheduled)
    return render_template('admin_panel.html', posts=posts, drafts=drafts, scheduled=scheduled, analytics=analytics, categories=categories, total_posts=total_posts, total_drafts=total_drafts, total_scheduled=total_scheduled)

@app.route('/admin/post/new', methods=['GET', 'POST'])
@admin_required
def add_post():
    categories = get_all_categories()
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        category_id = request.form.get('category_id')
        excerpt = request.form.get('excerpt')
        featured_image = request.form.get('featured_image')
        status = request.form.get('status', 'published')
        if title and content and category_id:
            post_id = create_post(title=title, content=content, category_id=category_id, author_id=session['user_id'], excerpt=excerpt, featured_image=featured_image, status=status)
            flash('Post created successfully!', 'success')
            return redirect(url_for('admin_panel'))
        else:
            flash('Please fill in all required fields.', 'error')
    return render_template('add_post.html', categories=categories)

@app.route('/admin/post/<int:post_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_post(post_id):
    post = get_post_by_id(post_id)
    if not post:
        abort(404)
    categories = get_all_categories()
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        category_id = request.form.get('category_id')
        excerpt = request.form.get('excerpt')
        featured_image = request.form.get('featured_image')
        status = request.form.get('status', 'published')
        if title and content and category_id:
            update_post(post_id=post_id, title=title, content=content, category_id=category_id, excerpt=excerpt, featured_image=featured_image, status=status)
            flash('Post updated successfully!', 'success')
            return redirect(url_for('admin_panel'))
        else:
            flash('Please fill in all required fields.', 'error')
    return render_template('edit_post.html', post=post, categories=categories)

@app.route('/admin/post/<int:post_id>/delete')
@admin_required
def delete_post_route(post_id):
    post = get_post_by_id(post_id)
    if post:
        delete_post(post_id)
        flash('Post deleted successfully!', 'success')
    else:
        flash('Post not found.', 'error')
    return redirect(url_for('admin_panel'))

@app.route('/admin/category/new', methods=['POST'])
@admin_required
def add_category():
    name = request.form.get('name')
    description = request.form.get('description')
    color = request.form.get('color', '#6366f1')
    if name:
        if create_category(name, description, color):
            flash('Category created successfully!', 'success')
        else:
            flash('Category already exists.', 'error')
    return redirect(url_for('admin_panel'))

@app.route('/admin/analytics')
@admin_required
def admin_analytics():
    analytics = get_analytics_summary()
    popular_posts = get_popular_posts(10)
    categories = get_all_categories()
    return render_template('admin_analytics.html', analytics=analytics, popular_posts=popular_posts, categories=categories)

@app.errorhandler(404)
def page_not_found(e):
    categories = get_all_categories()
    popular_posts = get_popular_posts(3)
    return render_template('404.html', categories=categories, popular_posts=popular_posts), 404

@app.route('/simple')
def simple():
    return render_template('simple_test.html')

if __name__ == '__main__':
    app.run(debug=True)