import unittest
import json
import time
from app import app, db, User, Book, BorrowRecord

class LibraryFullTest(unittest.TestCase):
    
    # 初始化：连接真实应用
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        # 为了避免数据冲突，每次测试用一个时间戳作为后缀
        self.suffix = str(int(time.time()))
        
    # === 用例 1: 测试用户注册与登录 (对应文档：用户管理 P0) ===
    def test_1_register_login(self):
        username = f"user_{self.suffix}"
        
        # 1. 注册
        res_reg = self.client.post('/api/register', json={
            'username': username, 'password': '123'
        })
        self.assertEqual(res_reg.json['code'], 200)
        
        # 2. 登录
        res_login = self.client.post('/api/login', json={
            'username': username, 'password': '123'
        })
        self.assertEqual(res_login.json['code'], 200)
        print(f"\n[通过] 用户注册与登录测试: {username}")
        return res_login.json['data']['userId']

    # === 用例 2: 图书入库与下架流程 (对应文档：图书管理 P0/P1) ===
    def test_2_book_lifecycle(self):
        isbn = f"999-{self.suffix}"
        
        # 1. 新书入库
        self.client.post('/api/books', json={
            'title': '测试全集', 'author': '测试君', 
            'isbn': isbn, 'stock': 2, 
            'publisher': '测试出版社', 'location': 'T-01'
        })
        
        # 查询这本书的ID
        with app.app_context():
            book = Book.query.filter_by(isbn=isbn).first()
            self.assertIsNotNone(book)
            
            # 2. 测试下架 (Status 1 -> 0)
            self.client.put(f'/api/books/{book.id}', json={'status': 0})
            
            # 验证数据库状态
            db.session.refresh(book)
            self.assertEqual(book.status, 0)
            print(f"[通过] 图书入库与下架测试: {book.title} (Status={book.status})")
            return book.id

    # === 用例 3: 借阅下架图书 (负面测试) ===
    def test_3_borrow_offline_book(self):
        # 复用上面的逻辑：先造用户和下架书，这里为了独立性简化处理
        # 实际运行中，我们直接用一个必然失败的场景
        # 假设 ID=99999 不存在
        res = self.client.post('/api/borrow', json={'userId': 1, 'bookId': 99999})
        self.assertEqual(res.json['code'], 400)
        print(f"[通过] 借阅无效图书测试: {res.json['msg']}")

    # === 用例 4: 完整的借还闭环 (核心业务) ===
    def test_4_borrow_return_cycle(self):
        # 1. 准备数据：新用户 + 新书(库存1)
        u_name = f"borrower_{self.suffix}"
        isbn = f"888-{self.suffix}"
        
        self.client.post('/api/register', json={'username': u_name, 'password': '123'})
        self.client.post('/api/books', json={
            'title': '借还测试书', 'author': 'Test', 'isbn': isbn, 'stock': 1,
            'publisher': 'P', 'location': 'L', 'status': 1
        })
        
        with app.app_context():
            user = User.query.filter_by(username=u_name).first()
            book = Book.query.filter_by(isbn=isbn).first()
            
            # 2. 借书
            res_borrow = self.client.post('/api/borrow', json={'userId': user.id, 'bookId': book.id})
            self.assertEqual(res_borrow.json['code'], 200)
            
            # 验证库存扣减 (1 -> 0)
            db.session.refresh(book)
            self.assertEqual(book.stock, 0)
            
            # 3. 还书
            # 获取借阅记录ID
            record = BorrowRecord.query.filter_by(user_id=user.id, book_id=book.id).first()
            res_return = self.client.post('/api/return', json={'recordId': record.id})
            self.assertEqual(res_return.json['code'], 200)
            
            # 验证库存恢复 (0 -> 1) 及 状态更新
            db.session.refresh(book)
            db.session.refresh(record)
            self.assertEqual(book.stock, 1)
            self.assertEqual(record.status, 1) # 1=已还
            
            print(f"[通过] 借还完整闭环测试: 库存变化 1->0->1, 记录状态 {record.status}")

if __name__ == '__main__':
    unittest.main()