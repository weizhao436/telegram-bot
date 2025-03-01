import os

class Config:
    # Telegram Bot Token
    BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
    
    # Flask Secret Key
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    
    # Database Configuration
    DATABASE = 'bot_data.db'
    
    # Media Storage Configuration
    MEDIA_FOLDER = 'media'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'mp4', 'pdf'}
    
    # Admin Interface Settings
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'password')

config = Config()
