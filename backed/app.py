from flask import Flask
from flask_cors import CORS
from flask import request, jsonify
from langchain_community.document_loaders import PyPDFLoader
from utils.ollama_client import ask_ai
from utils.auth import generate_token
from config import Config
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate

app = Flask(__name__)
CORS(app)
app.config.from_object(Config) 
db.init_app(app)

# 在db初始化后添加
migrate = Migrate(app, db)

@app.route('/api/upload',methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "亲爱的用户，非常抱歉我们没有读取到你的文件"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "亲爱的用户，非常抱歉我们读取的文件发现这是一个空文件"}), 400
    # 解析PDF文本
    text_content = parse_pdf(file.stream)
    
    # 调用DeepSeek生成摘要
    prompt = f"请用中文为以下文档生成3个标签和一句话摘要：\n{text_content[:2000]}"
    ai_response = ask_ai(prompt)
    
    return jsonify({
        "content": text_content,
        "ai_suggestion": ai_response
    })

@app.route('/api/ask', methods=['POST'])
def ask_question():
    data = request.json
    user_question = data.get('question')
    
    response = ask_ai(f"请基于以下知识库回答：{user_question}")
    return jsonify({"answer": response})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "用户名或密码不能为空"}), 401
    
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "用户名或密码错误"}), 401

    # 生成token
    token = generate_token(username)
    return jsonify({
        "message": "登录成功",
        "data": token
    }), 200

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    # 添加邮箱验证
    if not all([username, password, email]):
        return jsonify({"error": "用户名、密码和邮箱不能为空"}), 400

    # 添加邮箱重复检查
    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({"error": "用户名或邮箱已存在"}), 400

    try:
        new_user = User(username=username, email=email) 
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "注册成功", "user_id": new_user.id}), 201 

@app.route('/api/protected', methods=['GET'])
def protected_route():
    # 检查token
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "未提供token"}), 401

    # 解码token
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        username = payload['sub']
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "token已过期"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "无效的token"}), 401

    # 检查用户是否存在
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "用户不存在"}), 401

    return jsonify({"message": "您已通过身份验证"}), 200     

@app.route('/')
def hello():
    return "<h1>Hello World</h1>"

if __name__ == '__main__':
    app.run(debug=True)