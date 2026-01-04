from app import app, db

with app.app_context():
    db.drop_all()    # 删除所有旧表
    db.create_all()  # 按新代码重新建表
    print("数据库已重置：旧表删除，新表创建成功！")