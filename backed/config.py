import os
from pathlib import Path 

BASE_DIR = Path(__file__).parent.resolve() 

class Config:
    # 修正路径拼接方式（使用Path对象）
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR / 'database.db'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-123'
