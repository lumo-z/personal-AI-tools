from flask import Flask,Response
from flask_cors import CORS
from flask import request, jsonify
from langchain_community.document_loaders import PyPDFLoader
from utils.ollama_client import ask_ai
from utils.auth import generate_token
from config import Config
from models import db, User,ChatRecord
import json
import re
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
import jwt  # 添加jwt模块导入

app = Flask(__name__)
CORS(
    app,
    resources={
        r"/api/*": {
            "origins": ["http://localhost:8080"],
            "methods": ["GET", "POST", "OPTIONS"],  # SSE 通常用 GET
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "expose_headers": [], 
        }
    }
)
app.config.from_object(Config) 
db.init_app(app)

# 在db初始化后添加
migrate = Migrate(app, db)

def check_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "未提供token"}), 401
        try:
            payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            username = payload['sub']
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "token已过期"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "无效的token"}), 401
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({"error": "用户不存在"}), 401
        return f(*args, **kwargs)
    return decorated

class SSEEvent:
    """
    SSE事件封装类，确保符合规范
    """
    @staticmethod
    def create(event_type: str, data: dict) -> str:
        """
        生成符合SSE规范的事件字符串
        :param event_type: 事件类型 (status/think/message/error)
        :param data: 要发送的数据字典
        :return: 格式化后的SSE字符串
        """
        event_str = f"event: {event_type}\n"
        data_str = json.dumps(data, ensure_ascii=False)
        # 确保数据是单行 (SSE规范要求)
        data_str = data_str.replace("\n", "\\n")
        return f"{event_str}data: {data_str}\n\n"

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


@app.route('/api/ask/sse', methods=['GET', 'POST'])
def ask_question():
    """
    GET /api/ask/sse?question=xxx
    POST /api/ask/sse
    Request Body:
    {
        "question": "xxx"
    }
    Response:
    {
        "type": "message" | "think" | "error" | "status",
        "content": "xxx"
    }
    """
    # 获取问题参数
    if request.method == 'POST':
        user_question = request.json.get('question')
    else:
        user_question = request.args.get('question')
    
    if not user_question or len(user_question) > 1000:
        return jsonify({"error": "问题不能为空或超过1000字符"}), 400
    
    def generate_sse():
        try:
            # 发送开始事件
            yield SSEEvent.create("status", {"status": "start"})
            
            answer_buffer = ""
            min_chunk_size = 20  # 最小分块大小
            sentence_enders = ('。', '！', '？', '\n', '.', '!', '?')  # 句子结束符
            
            for chunk in ask_ai(user_question):
                if not chunk.strip():
                    continue
                
                # 处理思考内容
                if chunk.startswith('<think>'):
                    content = chunk[7:-8].strip()
                    if content:
                        yield SSEEvent.create("think", {"content": content})
                else:
                    # 处理回答内容
                    answer_buffer += chunk
                    
                    # 当缓冲区足够大或遇到句子结束符时发送
                    if (len(answer_buffer) >= min_chunk_size or 
                        any(punc in answer_buffer for punc in sentence_enders)):
                        yield SSEEvent.create("message", {"content": answer_buffer})
                        answer_buffer = ""
            
            # 发送剩余内容
            if answer_buffer:
                yield SSEEvent.create("message", {"content": answer_buffer})
            
            # 发送结束事件
            yield SSEEvent.create("status", {"status": "end"})
            
        except Exception as e:
            yield SSEEvent.create("error", {
                "error": str(e),
                "type": type(e).__name__
            })
            import traceback
            traceback.print_exc()

    return Response(
        generate_sse(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'  # 防止Nginx缓冲
        }
    )

@app.route('/api/login', methods=['POST'])
def login():
    """
    POST /api/login
    Request Body:
    {
        "username": "user1",
        "password": "password1"
    }
    """
    if request.method != 'POST':
        return jsonify({"error": "仅支持POST请求"}), 405
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
    """
    POST /api/register
    Request Body:
    {
        "username": "newuser",
        "password": "newpassword",
        "email": "xxxx",
        "telephone": "1234567890" 
    }
    """
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
@check_token  
def protected():
    """
    检查用户token是否具备访问权限
    GET /api/protected
    """
    current_user = get_jwt_identity()  # 获取当前用户的身份
    return jsonify({"message": f"这是受保护的资源，当前用户: {current_user}"}), 200

@app.route('/api/records', methods=['POST'])
def save_chat_record():
    """
    保存聊天记录
    POST /api/chat/records
    Request Body:
    {
        "user_id": 123,
        "session_id": "abc123",
        "question": "你好",
        "answer": "你好！有什么可以帮您的吗？"
    }
    """
    data = request.get_json()
    
    # 验证必要字段
    required_fields = ['user_id', 'session_id', 'question', 'answer']
    if not all(field in data for field in required_fields):
        return jsonify({'error': '缺少必要字段','data':data}), 400
    
    try:
        new_record = ChatRecord(
            user_id=data['user_id'],
            session_id=data['session_id'],
            question=data['question'],
            answer=data['answer']
        )
        db.session.add(new_record)
        db.session.commit()
        
        return jsonify({
            'message': '保存成功',
            'record_id': new_record.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/records/<int:user_id>', methods=['GET'])
def get_user_records(user_id):
    """
    获取指定用户的所有聊天记录
    GET /api/chat/records/<user_id>
    Query Parameters:
    - session_id: 可选，指定会话ID
    - limit: 可选，限制返回记录数量
    - offset: 可选，分页偏移量
    """
    try:
        # 获取查询参数
        session_id = request.args.get('session_id')
        limit = request.args.get('limit', default=30, type=int)
        offset = request.args.get('offset', default=0, type=int)
        
        # 构建基础查询
        query = ChatRecord.query.filter_by(user_id=user_id)
        
        # 如果提供了session_id，则添加过滤条件
        if session_id:
            query = query.filter_by(session_id=session_id)
        
        # 执行查询并应用分页
        records = query.order_by(ChatRecord.timestamp.desc()) \
                      .limit(limit).all()
        
        return jsonify({
            'count': len(records),
            'records': [record.to_dict() for record in records]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions', methods=['GET', 'OPTIONS'])
def get_user_sessions():
    """
    获取用户的所有会话列表
    GET /api/sessions?user_id=xxx
    """
    if request.method == 'OPTIONS':
        # 处理预检请求
        response = jsonify()
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:8080')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        return response
    
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': '缺少user_id参数'}), 400
            
        # 获取去重的会话ID列表
        sessions = ChatRecord.query.filter_by(user_id=user_id) \
            .with_entities(
                ChatRecord.session_id,
                db.func.max(ChatRecord.timestamp).label('last_active'),
                ChatRecord.question
            ) \
            .group_by(ChatRecord.session_id) \
            .order_by(db.desc('last_active')) \
            .all()
            
        return jsonify({
            'sessions': [{
                'session_id': session[0],
                'last_active': session[1].isoformat(),
                'title': session[2][:20] + '...' if len(session[2]) > 20 else session[2]
            } for session in sessions]
        }), 200
        
    except Exception as e:
        app.logger.error(f"获取会话列表失败: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/')
def hello():
    return "<h1>Hello World</h1>"
    
def parse_pdf(file_stream):
    """
    PDF解析函数
    """
    loader = PyPDFLoader(file_stream)
    pages = loader.load()
    return "\n".join([page.page_content for page in pages])

if __name__ == '__main__':
    app.run(debug=True)


