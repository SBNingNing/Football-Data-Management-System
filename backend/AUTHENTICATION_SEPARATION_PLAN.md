# 认证功能分离计划

## 概述

本文档描述了如何将游客登录和管理员登录功能分离，以支持未来的需求变更。

## 当前架构

### Token 类型标记
- 所有 JWT Token 现在包含 `type` 声明：
  - `guest`: 游客令牌
  - `user`: 普通用户令牌
  - `admin`: 管理员令牌

### 代码准备
1. **AuthService.create_token()** - 接受 `token_type` 参数
2. **get_token_type()** - 中间件辅助函数，用于获取令牌类型
3. **JWT additional_claims** - 所有令牌包含类型和用户ID信息

## 未来分离步骤

### 前端修改

#### 1. 创建独立的管理员登录页面
```vue
<!-- AdminLogin.vue -->
<template>
  <div class="admin-login">
    <h2>管理员登录</h2>
    <el-form @submit="handleAdminLogin">
      <el-form-item label="用户名">
        <el-input v-model="credentials.username" />
      </el-form-item>
      <el-form-item label="密码">
        <el-input v-model="credentials.password" type="password" />
      </el-form-item>
      <el-button type="primary" native-type="submit">登录</el-button>
    </el-form>
  </div>
</template>
```

#### 2. 分离路由
```javascript
// router/index.js
const routes = [
  {
    path: '/',
    component: Home,
    beforeEnter: (to, from, next) => {
      // 只允许游客访问
      const authStore = useAuthStore();
      authStore.guestLogin().then(() => next());
    }
  },
  {
    path: '/admin',
    component: AdminLayout,
    beforeEnter: (to, from, next) => {
      // 检查管理员权限
      const authStore = useAuthStore();
      if (authStore.user?.role === 'admin') {
        next();
      } else {
        next('/admin/login');
      }
    },
    children: [
      { path: 'login', component: AdminLogin },
      { path: 'dashboard', component: AdminDashboard }
    ]
  }
]
```

#### 3. 更新 AuthStore
```javascript
// store/modules/auth.js
export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    tokenType: localStorage.getItem('tokenType') || null, // 新增
    loading: false,
    error: null
  }),
  
  actions: {
    async guestLogin() {
      // 保持不变，自动游客登录
      const { token } = await guestLogin();
      this.token = token;
      this.tokenType = 'guest'; // 设置类型
      localStorage.setItem('tokenType', 'guest');
      setAuthToken(token);
    },
    
    async adminLogin(credentials) {
      // 管理员登录
      const { token, user } = await adminLogin(credentials);
      this.token = token;
      this.user = user;
      this.tokenType = 'admin'; // 设置类型
      localStorage.setItem('tokenType', 'admin');
      setAuthToken(token);
    }
  }
})
```

### 后端修改

#### 1. 创建专用的管理员登录端点（可选）
```python
@auth_bp.route('/admin/login', methods=['POST'])
@validate_json(['username', 'password'])
def admin_login_endpoint():
    """管理员专用登录端点"""
    payload = LoginIn(**(request.get_json() or {}))
    
    # 认证用户
    user, error = AuthService.authenticate_user(
        username=payload.username,
        password=payload.password
    )
    
    if error:
        return jsonify({'error': error}), 401
    
    # 验证管理员权限
    if user.身份_角色 != 'admin':
        logger.warning(f"Non-admin user {user.用户名} attempted admin login")
        return jsonify({'error': '需要管理员权限'}), 403
    
    # 创建管理员令牌
    access_token, token_error = AuthService.create_token(user.用户ID, 'admin')
    if token_error:
        return jsonify({'error': token_error}), 500
    
    out = LoginOut(access_token=access_token, user=UserView(**user.to_dict()))
    return jsonify(out.model_dump(by_alias=True)), 200
```

#### 2. 增强中间件以检查令牌类型
```python
def admin_only(f):
    """仅管理员访问（基于令牌类型）"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        token_type = get_token_type()
        
        if token_type != 'admin':
            logger.warning(f"Non-admin token type {token_type} attempted admin endpoint")
            return jsonify({'error': '需要管理员权限'}), 403
        
        return f(*args, **kwargs)
    return decorated_function
```

## 迁移路径

### 阶段 1：准备（当前状态）✅
- [x] Token 包含类型信息
- [x] 中间件支持获取令牌类型
- [x] 登录服务支持类型参数

### 阶段 2：前端分离（未来）
- [ ] 创建独立的管理员登录页面
- [ ] 更新路由守卫
- [ ] 在 AuthStore 中区分令牌类型
- [ ] 移除主页面的管理员登录入口

### 阶段 3：后端增强（未来）
- [ ] 创建专用的管理员登录端点
- [ ] 更新中间件以严格检查令牌类型
- [ ] 添加令牌刷新机制

### 阶段 4：测试和部署（未来）
- [ ] 全面测试游客和管理员流程
- [ ] 更新文档
- [ ] 逐步部署

## 兼容性说明

当前实现保持向后兼容：
- 旧的 Token 仍然有效（没有 type 声明时默认为 'user'）
- 现有登录流程不受影响
- 可以随时启动分离过程

## 安全考虑

1. **令牌类型验证**：确保管理员端点检查令牌类型
2. **权限双重验证**：除了令牌类型，还要验证数据库中的角色
3. **日志审计**：记录所有管理员访问尝试
4. **令牌过期**：考虑为管理员令牌设置较短的过期时间

## 示例代码

详见各模块的注释和实现。所有准备工作已经完成，可以在需要时快速实施分离。
