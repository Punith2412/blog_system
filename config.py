import os

class Config:
    """Application configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('DEBUG') or True
    DATABASE_PATH = os.environ.get('DATABASE_PATH') or 'blogdata.db'
    
    # Upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
    
    # Allowed extensions for image uploads
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Blog settings
    BLOG_TITLE = "Modern Blog"
    BLOG_DESCRIPTION = "A modern, minimalist blog built with Flask"
    POSTS_PER_PAGE = 9