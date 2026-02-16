# Football Data Management System - 后端架构文档

## 1. 架构概览

本项目后端采用现代化的 **Flask** 应用架构，遵循 **分层架构 (Layered Architecture)** 原则。旨在实现高内聚、低耦合、易于维护和扩展的代码结构。

### 核心技术栈
- **Web 框架**: Flask (Python)
- **数据库 ORM**: SQLAlchemy
- **数据校验与序列化**: Pydantic v2
- **认证授权**: Flask-JWT-Extended
- **数据库**: MySQL 8.0+

---

## 2. 目录结构与分层说明

后端代码主要组织在 `app/` 目录下，各层级职责划分如下：

```text
backend/
├── app/
│   ├── routes/          # [表现层/控制器] 处理 HTTP 请求与响应
│   ├── services/        # [业务逻辑层] 核心业务处理、事务管理
│   ├── schemas/         # [数据传输层] Pydantic 模型，负责输入校验与输出序列化
│   ├── models/          # [数据持久层] SQLAlchemy ORM 模型，映射数据库表
│   ├── middleware/      # [中间件层] 全局请求处理（认证、日志、错误捕获）
│   ├── utils/           # [基础设施/工具] 通用工具函数、日志配置
│   ├── config.py        # 全局配置管理
│   ├── database.py      # 数据库连接与 Session 管理
│   └── extensions.py    # 第三方插件初始化
├── logs/                # 应用运行日志
├── run.py               # 应用启动入口
└── requirements.txt     # Python 依赖清单
```

---

## 3. 各层级详细说明

### 3.1 表现层 (Routes / Controllers)
- **位置**: `app/routes/`
- **职责**: 
  - 定义 URL 路由端点 (Endpoints)。
  - 解析 HTTP 请求参数（Query String, Body, Path Params）。
  - 调用 `Service` 层处理业务。
  - 使用 `Schema` 层格式化返回数据。
  - **原则**: **不包含**复杂的业务逻辑，只负责“收发信件”。

### 3.2 业务逻辑层 (Services)
- **位置**: `app/services/`
- **职责**:
  - 封装核心业务规则（如：计算积分、判定胜负、跨表数据聚合）。
  - 管理数据库事务（Commit/Rollback）。
  - 调用 `Model` 层进行原子性的数据库操作。
  - 处理异常情况并返回标准化的结果对象。
- **原则**: 业务逻辑的核心，应当是独立于 HTTP 上下文的纯 Python 类/函数。

### 3.3 数据传输层 (Schemas / DTOs)
- **位置**: `app/schemas/`
- **职责**:
  - **输入校验 (Input Validation)**: 验证前端发送的数据格式（如邮箱格式、必填项）。
  - **输出序列化 (Output Serialization)**: 定义接口返回的数据结构，过滤敏感字段（如密码哈希）。
  - 使用 `Pydantic` 定义强类型的 Request/Response 模型。

### 3.4 数据持久层 (Models)
- **位置**: `app/models/`
- **职责**:
  - 定义数据库表结构（Table Schema）。
  - 定义表之间的关联关系（Relationship, ForeignKey）。
  - 提供基础的 ORM 操作对象。

### 3.5 中间件层 (Middleware)
- **位置**: `app/middleware/`
- **职责**:
  - **Auth Middleware**: 处理 JWT Token 验证。
  - **Context Middleware**: 管理请求上下文。
  - **Stats/Log Middleware**: 记录请求耗时、审计日志。
  - **Security Headers**: 添加安全响应头。

---

## 4. 关键工作流示例

以 **"获取球队历史 (Get Team History)"** 为例：

1.  **Request**: 用户发送 `GET /api/team-history/{id}/complete`。
2.  **Route (`routes/team_history.py`)**: 
    - 接收请求，解析 `id`。
    - 调用 `TeamHistoryService.get_team_complete_history(id)`。
3.  **Service (`services/team_history_service.py`)**:
    - 开启数据库 Session。
    - 查询 `Team` 表获取基本信息。
    - 聚合查询 `Match`, `Tournament` 表计算胜率、进球数。
    - 组装字典数据。
4.  **Schema (`schemas/team_history.py`)**:
    - Route 层使用 `TH_TeamCompleteHistoryOut` 模型对 Service 返回的数据进行校验和转换（如下划线命名规范化）。
5.  **Response**: 返回标准 JSON 格式给前端。

---

## 5. 环境配置与启动

### 5.1 前置要求
- Python 3.8+
- MySQL 8.0+

### 5.2 安装依赖
推荐使用虚拟环境：

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
.\venv\Scripts\activate

# 激活虚拟环境 (Linux/Mac)
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 5.3 环境变量配置
在 `backend/` 目录下创建 `.env` 文件（或设置系统环境变量）：

```ini
FLASK_ENV=development
SECRET_KEY=your_secret_key
DATABASE_URI=mysql+pymysql://user:password@localhost/football_db
```

### 5.4 启动后端
在 `backend/` 目录下执行：

```bash
python run.py
```

服务默认运行在 `http://0.0.0.0:5000`。
