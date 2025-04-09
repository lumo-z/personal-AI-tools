from flask import Flask,Response
from flask_cors import CORS
from flask import request, jsonify
from langchain_community.document_loaders import PyPDFLoader
from utils.ollama_client import ask_ai
from utils.auth import generate_token
from config import Config
from models import db, User
import json
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
import jwt  # 添加jwt模块导入

app = Flask(__name__)
CORS(app)
app.config.from_object(Config) 
db.init_app(app)

# 在db初始化后添加
migrate = Migrate(app, db)

# 文件上传接口需要添加文件类型检查
@app.route('/api/upload',methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "文件未提供"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "空文件"}), 400
    if not file.filename.lower().endswith('.pdf'):  # 添加文件类型检查
        return jsonify({"error": "仅支持PDF文件"}), 400
    # 解析PDF文本
    text_content = parse_pdf(file.stream)
    
    # 调用DeepSeek生成摘要
    prompt = f"请用中文为以下文档生成3个标签和一句话摘要：\n{text_content[:2000]}"
    ai_response = ask_ai(prompt)
    
    return jsonify({
        "content": text_content,
        "ai_suggestion": ai_response
    })

@app.route('/api/ask', methods=['POST', 'GET'])
@app.route('/api/ask/sse', methods=['GET'])
def ask_question():
    # 获取问题参数
    if request.method == 'POST':
        user_question = request.json.get('question')
    else:
        user_question = request.args.get('question')
    
    if not user_question or len(user_question) > 1000:
        return jsonify({"error": "问题不能为空或超过1000字符"}), 400

    # 如果是普通请求
    if request.path == '/api/ask':
        try:
            response = ask_ai(f"请基于知识库回答以下问题：{user_question}")
            return jsonify({"answer": response, "message": "回答成功"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    # 如果是SSE请求
    def generate_sse():
        try:
            yield f"event: status\ndata: {json.dumps({'status': 'start'})}\n\n"
            think_msg = "正在分析问题..."
            yield f"event: think\ndata: {json.dumps({'content': think_msg})}\n\n"
            
            for chunk in ask_ai(user_question):
                if chunk.startswith('<think>'):
                    content = chunk[7:-8].strip()
                    yield f"event: think\ndata: {json.dumps({'content': content})}\n\n"
                else:
                    yield f"event: message\ndata: {json.dumps({'content': chunk})}\n\n"
                    
            yield f"event: status\ndata: {json.dumps({'status': 'end'})}\n\n"
        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

    return Response(generate_sse(), mimetype='text/event-stream')

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
        "code": 200,
        "message": "登录成功",
        "data": {
            "token": token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "telephone": user.telephone
            }
        }
    }), 200

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    telephone = data.get('telephone')
    email = data.get('email')

    # 添加邮箱验证
    if not all([username, password, email]):
        return jsonify({"error": "用户名、密码和邮箱不能为空"}), 400

    # 添加邮箱重复检查
    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({"error": "用户名或邮箱已存在"}), 400

    try:
        new_user = User(username=username, email=email, telephone=telephone) 
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error during registration: {e}")
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
    
def parse_pdf(file_stream):
    """PDF解析函数"""
    loader = PyPDFLoader(file_stream)
    pages = loader.load()
    return "\n".join([page.page_content for page in pages])

CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:8080"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})
if __name__ == '__main__':
    app.run(debug=True)


