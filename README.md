# 基于 AI 辅助开发的图书馆管理系统

## 1. 项目简介
本项目是一个前后端分离的轻量级图书馆管理系统，包含用户注册登录、图书增删改查、借还书流程、权限管理等核心功能。
前端采用 Vue 3 + Element Plus，后端采用 Python Flask + MySQL 8.0。

## 2. 依赖清单
请查看 `requirements.txt` 文件。核心依赖包括：
- Flask
- Flask-SQLAlchemy
- PyMySQL
- Flask-Cors

## 3. 运行说明
1. **配置数据库**：确保本地安装 MySQL 8.0，创建数据库 `library_db`，并在 `app.py` 中修改数据库账号密码。
2. **安装依赖**：
   ```bash
   pip install -r requirements.txt