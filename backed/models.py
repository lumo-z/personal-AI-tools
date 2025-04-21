from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telephone = db.Column(db.String(15))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    password_hash = db.Column(db.String(256))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"

class ChatRecord(db.Model):
    """
    聊天记录数据模型
    """
    __tablename__ = 'chat_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)  # 用户ID，添加索引提高查询效率
    session_id = db.Column(db.String(64), nullable=False)  # 会话ID，用于区分不同对话会话
    question = db.Column(db.Text, nullable=False)  # 用户提问，使用Text类型存储更长的内容
    answer = db.Column(db.Text, nullable=False)  # AI回答
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)  # 时间戳，添加索引
    
    # 添加模型到字符串的转换方法
    def __repr__(self):
        return f'<ChatRecord {self.id} - User {self.user_id}>'
    
    def to_dict(self):
        """将模型转换为字典，便于JSON序列化"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'question': self.question,
            'answer': self.answer,
            'timestamp': self.timestamp.isoformat()
        }
