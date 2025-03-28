from datetime import datetime, timedelta
import jwt
from config import Config

def generate_token(username):
    """生成JWT令牌"""
    payload = {
        'sub': username,
        'exp': datetime.utcnow() + timedelta(hours=2)
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')