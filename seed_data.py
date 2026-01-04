# seed_data.py
from app import app, db, User, Book

def seed():
    with app.app_context():
        # 1. 创建管理员和普通用户 (对应文档要求：支持学生/教师注册)
        if not User.query.filter_by(username='admin').first():
            # 模拟加密存储（文档要求加盐加密，这里简化演示，实际代码中通常用 werkzeug.security）
            admin = User(username='admin', password='123', role='admin') 
            user1 = User(username='student1', password='123', role='user')
            db.session.add_all([admin, user1])
            print("账号创建成功: admin (管理员), student1 (学生)")
        
        # 2. 创建测试图书 (补全 Publisher 和 Location)
        books_data = [
            {"title": "软件工程导论", "isbn": "978-7-111", "author": "张海藩", "publisher": "清华大学出版社", "stock": 5, "location": "A区-01架"},
            {"title": "深入浅出MySQL", "isbn": "978-7-121", "author": "唐汉明", "publisher": "人民邮电出版社", "stock": 2, "location": "B区-03架"},
            {"title": "Python编程", "isbn": "978-7-115", "author": "Eric", "publisher": "机械工业出版社", "stock": 10, "location": "A区-02架"}
        ]
        
        for b in books_data:
            if not Book.query.filter_by(isbn=b['isbn']).first():
                book = Book(
                    title=b['title'], 
                    isbn=b['isbn'], 
                    author=b['author'], 
                    publisher=b['publisher'], # 新增
                    stock=b['stock'],
                    location=b['location'],   # 新增
                    status=1 # 默认上架
                )
                db.session.add(book)
                print(f"图书添加成功: {b['title']}")
        
        db.session.commit()
        print("所有测试数据注入完毕！")

if __name__ == '__main__':
    seed()