# 📚 基于 AI 辅助开发的图书馆管理系统 (Library Management System)

## 1. 项目简介
本项目是一个前后端分离的轻量级图书馆管理系统，旨在演示软件工程全流程（需求、设计、编码、测试）与 AI 辅助开发的结合。系统实现了图书入库、借阅、归还、搜索、以及用户权限管理（管理员/普通读者）等核心功能。

**核心技术栈：**
- **后端**：Python 3.9 + Flask + Flask-SQLAlchemy + PyMySQL
- **前端**：Vue 3 (CDN引入) + Element Plus
- **数据库**：MySQL 8.0
- **开发工具**：VS Code + Copilot/Gemini

---

## 2. 环境准备
在运行本项目前，请确保您的电脑已安装以下环境：
1.  **Python 3.8 或以上版本**
2.  **MySQL 8.0 数据库**

---

## 3. 快速启动 (运行说明)

### 第一步：配置数据库
1.  打开您的 MySQL 管理工具（如 Navicat, Workbench 或命令行）。
2.  新建一个空的数据库，命名为 `library_db`：

    CREATE DATABASE library_db CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

3.  **【非常重要】修改连接配置**：
    打开项目根目录下的 `app.py` 文件，找到第 13 行左右，将数据库连接字符串中的 `root:123456` 修改为您本地 MySQL 的**真实用户名和密码**：

    # 格式：mysql+pymysql://用户名:密码@地址:端口/数据库名
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:您的密码@localhost/library_db'

### 第二步：安装依赖
在项目根目录下打开终端（Terminal），执行以下命令安装所需 Python 库：

    pip install -r requirements.txt

*(如果尚未创建 requirements.txt，可执行：pip install Flask Flask-SQLAlchemy PyMySQL Flask-Cors)*

### 第三步：初始化数据
本项目提供了自动初始化脚本，无需手动建表。请在终端依次执行：

1.  **重置并创建表结构**：

    python reset_db.py

    *（成功会显示：数据库已重置...）*

2.  **注入测试数据**（包含管理员账号和测试图书）：

    python seed_data.py

    *（成功会显示：所有测试数据注入完毕！）*

### 第四步：启动后端服务
在终端执行以下命令启动 Flask 服务器：

    python app.py

当看到 `Running on http://127.0.0.1:5000` 字样时，表示后端启动成功。**注意：请勿关闭此终端窗口，否则服务会停止。**

### 第五步：访问前端页面
1.  找到项目文件夹中的 `index.html` 文件。
2.  **直接双击打开**（或右键选择 Chrome/Edge 浏览器打开）。
3.  即可开始使用系统。

---

## 4. 测试账号说明

为方便演示，初始化脚本 (`seed_data.py`) 默认创建了以下账号：

| 角色 | 用户名 | 密码 | 权限说明 |
| :--- | :--- | :--- | :--- |
| **管理员** | `admin` | `123` | 拥有最高权限：新书入库、图书下架/编辑、查看全员借阅记录 |
| **普通用户** | `student1` | `123` | 基础权限：查询图书、借阅、归还、查看个人记录 |
| **新用户** | (自行注册) | (自定) | 可通过登录页面的“去注册”功能创建新账号 |

---

## 5. 自动化测试
本项目包含完整的单元测试与集成测试脚本，覆盖了注册、入库、借还闭环等核心场景。
运行测试命令：

    python test_full.py

**预期结果**：控制台输出 `OK`，且无报错信息。这证明了核心业务逻辑的正确性。

---

## 6. 目录结构说明

    library_system/
    ├── app.py              # 后端核心入口 (Flask API + ORM模型)
    ├── index.html          # 前端单页面 (Vue3 + ElementPlus)
    ├── requirements.txt    # Python依赖清单
    ├── reset_db.py         # 数据库重置脚本 (工具)
    ├── seed_data.py        # 测试数据生成脚本 (工具)
    ├── test_full.py        # 自动化测试脚本 (测试报告来源)
    └── README.md           # 项目运行说明文档

## 7. 常见问题 (FAQ)
* **Q: 启动时报错 `Access denied for user 'root'@'localhost'`**
    * A: 这是数据库密码错误。请检查 `app.py` 里的数据库密码是否改成了您电脑上 MySQL 的正确密码。
* **Q: 页面提示“连接服务器失败”**
    * A: 请确认后端黑窗口（终端）是否一直开着。前端页面只是界面，必须依靠后端的 `app.py` 提供数据服务。
* **Q: 安装依赖慢或超时**
    * A: 可以尝试使用国内镜像源安装：
      pip install -r requirements.txt -i [https://pypi.tuna.tsinghua.edu.cn/simple](https://pypi.tuna.tsinghua.edu.cn/simple)
