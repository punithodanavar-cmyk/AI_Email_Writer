import os
from dotenv import load_dotenv

# ✅ Ensure .env loads properly
load_dotenv(dotenv_path=".env")

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_ENV') == 'development'
    
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DB = os.getenv('MYSQL_DB', 'email_writer_db')
    
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# 🔥 DEBUG (remove later)
print("✅ Loaded GROQ API KEY:", os.getenv('GROQ_API_KEY'))