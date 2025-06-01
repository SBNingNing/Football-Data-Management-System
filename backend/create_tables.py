from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    # 创建所有表
    db.create_all()
    print("数据库表创建成功！")
    
    # 创建管理员用户（可选）
    admin_user = User.query.filter_by(用户名='admin').first()
    if not admin_user:
        admin = User(
            用户名='admin',
            邮箱='admin@example.com',
            身份_角色='admin',
            状态='A'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("管理员账户创建成功：用户名=admin，密码=admin123")
    else:
        print("管理员账户已存在")
