# 足球数据管理系统运行指南

## 1. 数据库配置

### 1.1 连接本地 MySQL 数据库
确保本地已安装并启动 MySQL 服务。

### 1.2 修改数据库连接配置
修改位于 `backend/app/__pycache__/config.py` 中的数据库连接配置：

```python
# 将 SQLALCHEMY_DATABASE_URI 变量中的 xxx 部分修改为您的 MySQL 密码
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:your_password@localhost/football_management_system"
```

### 1.3 导入数据库文件
在 MySQL 中导入 `football.sql` 文件：

```sql
-- 在 MySQL 命令行或图形界面中执行
SOURCE path/to/football.sql;
```

## 2. 启动系统

### 2.1 启动前后端服务
在项目根目录下执行以下命令：

```bash
python install_and_run.py
```

### 2.2 访问系统
前后端启动成功后，可通过以下方式访问：

- 点击 `install_and_run.py` 文件中的链接：`http://localhost:3000`
- 或直接在浏览器中输入：`http://localhost:3000`

## 3. 系统使用

网页正常加载后，请参考系统功能展示文档进行各项功能的使用和测试。
管理员账号：ustc
管理员密码：ustc1958

## 注意事项

- 确保 MySQL 服务正在运行
- 检查防火墙设置，确保端口 3000 可访问
- 如遇到依赖包问题，请检查 Python 环境和相关依赖是否正