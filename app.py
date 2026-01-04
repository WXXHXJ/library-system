from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# 数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/library_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ================= 模型定义 (不变) =================
# 对应文档 Source 49-55
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, comment='用户ID')
    username = db.Column(db.String(50), unique=True, nullable=False, comment='用户名')
    password = db.Column(db.String(255), nullable=False, comment='加密后的密码')
    role = db.Column(db.String(10), default='user', comment='角色: admin/user')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')

# 对应文档 Source 57-66
class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True, comment='图书ID')
    title = db.Column(db.String(100), nullable=False, comment='书名')
    author = db.Column(db.String(50), nullable=False, comment='作者')
    isbn = db.Column(db.String(20), unique=True, comment='ISBN号')
    publisher = db.Column(db.String(100), comment='出版社')     # <--- 新增字段
    stock = db.Column(db.Integer, default=1, comment='库存数量')
    location = db.Column(db.String(50), comment='馆藏位置')     # <--- 新增字段
    status = db.Column(db.Integer, default=1, comment='状态 1:上架 0:下架') # <--- 新增字段

# 对应文档 Source 68-77
class BorrowRecord(db.Model):
    __tablename__ = 'borrow_records'
    id = db.Column(db.Integer, primary_key=True, comment='记录ID')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='关联用户ID')
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False, comment='关联图书ID')
    borrow_date = db.Column(db.DateTime, default=datetime.now, comment='借出时间')
    return_date = db.Column(db.DateTime, nullable=True, comment='归还时间')
    status = db.Column(db.Integer, default=0, comment='状态 0:未还 1:已还') # <--- 对应文档要求

# app.py (后半部分：业务接口)

# ================= 业务接口 (严格对应文档功能表 Source 32) =================

@app.route('/init_db')
def init_db():
    db.create_all()
    return "数据库表结构已就绪！"

# --- 1. 用户管理模块 (对应文档：注册与登录 P0) ---

# [新增] 用户注册接口
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({"code": 400, "msg": "用户名已存在"})
    
    new_user = User(
        username=data.get('username'),
        password=data.get('password'), # 实际应加密
        role=data.get('role', 'user')  # 默认注册为普通用户
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"code": 200, "msg": "注册成功"})

# 用户登录接口 (对应文档 API列表 Source 80)
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    # 查询匹配用户名和密码
    user = User.query.filter_by(username=data.get('username'), password=data.get('password')).first()
    if user:
        return jsonify({
            "code": 200, 
            "msg": "登录成功", 
            "data": {"userId": user.id, "role": user.role, "username": user.username}
        })
    return jsonify({"code": 401, "msg": "用户名或密码错误"})

# --- 2. 图书管理模块 (对应文档：入库、查询、编辑、下架) ---

# 图书查询接口 (对应文档 Source 32: 支持书名、作者模糊搜索)
@app.route('/api/books', methods=['GET'])
def get_books():
    keyword = request.args.get('keyword', '')
    query = Book.query
    
    # 如果有搜索词，同时匹配书名或作者
    if keyword:
        query = query.filter(
            (Book.title.like(f'%{keyword}%')) | 
            (Book.author.like(f'%{keyword}%'))
        )
    
    # 只显示状态为 1 (上架) 的书，或者管理员后台可以看到所有(此处简化为只看上架)
    query = query.filter_by(status=1) 
    
    books = query.all()
    return jsonify({
        "code": 200, 
        "data": [{
            "id": b.id, 
            "title": b.title, 
            "author": b.author, 
            "isbn": b.isbn, 
            "publisher": b.publisher, # 新增字段
            "location": b.location,   # 新增字段
            "stock": b.stock
        } for b in books]
    })

# 图书入库接口 (对应文档 Source 32: 管理员录入新书 P0)
@app.route('/api/books', methods=['POST'])
def add_book():
    data = request.json
    # 简单的去重检查
    if Book.query.filter_by(isbn=data.get('isbn')).first():
        return jsonify({"code": 400, "msg": "该ISBN已存在"})
    
    new_book = Book(
        title=data.get('title'),
        author=data.get('author'),
        isbn=data.get('isbn'),
        publisher=data.get('publisher'), # 补全
        location=data.get('location'),   # 补全
        stock=data.get('stock', 1),
        status=1 # 默认为上架
    )
    db.session.add(new_book)
    db.session.commit()
    return jsonify({"code": 200, "msg": "图书入库成功"})

# [新增] 图书编辑/下架接口 (对应文档 Source 32: 编辑/下架 P1)
@app.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.json
    book = db.session.get(Book, book_id)
    if not book:
        return jsonify({"code": 404, "msg": "图书不存在"})
    
    # 如果请求包含 status=0，则是“下架”操作
    if 'status' in data:
        book.status = data['status']
    
    # 更新其他信息
    if 'stock' in data: book.stock = data['stock']
    if 'location' in data: book.location = data['location']
    
    db.session.commit()
    return jsonify({"code": 200, "msg": "图书信息更新成功"})

# --- 3. 借阅管理模块 (对应文档：借书、还书、记录) ---

# 借书接口 (对应文档 Source 32: 校验库存、生成记录 P0)
@app.route('/api/borrow', methods=['POST'])
def borrow_book():
    data = request.json
    try:
        book = db.session.get(Book, data.get('bookId'))
        # 核心校验：书是否存在、是否上架、库存是否足够
        if not book or book.status == 0 or book.stock < 1:
            return jsonify({"code": 400, "msg": "库存不足或图书已下架"})
        
        # 1. 扣减库存
        book.stock -= 1
        
        # 2. 生成借阅记录 (状态 0:未还)
        record = BorrowRecord(
            user_id=data.get('userId'), 
            book_id=book.id,
            status=0 # 对应文档 Source 74
        )
        db.session.add(record)
        db.session.commit()
        return jsonify({"code": 200, "msg": "借阅成功"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "msg": str(e)})

# 还书接口 (对应文档 Source 32: 恢复库存 P0)
@app.route('/api/return', methods=['POST'])
def return_book():
    data = request.json
    record_id = data.get('recordId')
    
    try:
        record = db.session.get(BorrowRecord, record_id)
        if not record or record.status == 1: # 状态 1:已还
            return jsonify({"code": 400, "msg": "记录无效或已归还"})
        
        # 1. 更新记录状态
        record.return_date = datetime.now()
        record.status = 1 # 标记为已还 (对应文档 Source 74)
        
        # 2. 恢复图书库存
        book = db.session.get(Book, record.book_id)
        book.stock += 1
        
        db.session.commit()
        return jsonify({"code": 200, "msg": "归还成功"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "msg": str(e)})

# 借阅记录查询 (对应文档 Source 32: 查看历史 P1)
@app.route('/api/records', methods=['GET'])
def get_my_records():
    user_id = request.args.get('userId')
    # 查询该用户的所有记录，按时间倒序
    records = BorrowRecord.query.filter_by(user_id=user_id).order_by(BorrowRecord.borrow_date.desc()).all()
    
    result = []
    for r in records:
        book = db.session.get(Book, r.book_id)
        result.append({
            "id": r.id,
            "bookTitle": book.title,
            "borrowDate": r.borrow_date.strftime('%Y-%m-%d %H:%M'),
            "returnDate": r.return_date.strftime('%Y-%m-%d %H:%M') if r.return_date else None,
            "status": "已归还" if r.status == 1 else "借阅中" # 对应文档状态码
        })
    return jsonify({"code": 200, "data": result})

if __name__ == '__main__':
    app.run(debug=True, port=5000)