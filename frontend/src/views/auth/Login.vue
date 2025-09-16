<template>
  <div class="login-container">
    <div class="auth-container">
      <h2 class="auth-title">科大校园足球赛事管理系统</h2>
      
      <!-- 登录选项卡 -->
      <el-tabs v-model="activeTab" class="login-tabs" @tab-change="handleTabChange">
        <el-tab-pane label="游客访问" name="guest">
          <div class="guest-content">
            <div class="guest-icon">
              <el-icon size="60"><User /></el-icon>
            </div>
            <p class="guest-description">无需注册，直接访问足球赛事信息</p>
            <el-button 
              type="primary" 
              size="large"
              style="width: 100%" 
              :loading="guestLoading || authStore.loading"
              @click="guestLogin"
>
              <el-icon><Right /></el-icon>
              游客进入
            </el-button>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="管理员登录" name="admin">
          <el-form :model="loginForm" :rules="rules" ref="loginFormRef" label-position="top" @submit.prevent="submitForm">
            <el-form-item label="管理员账号" prop="username">
              <el-input 
                v-model="loginForm.username" 
                prefix-icon="UserFilled" 
                placeholder="请输入管理员账号"
                size="large"
>
              </el-input>
            </el-form-item>
            
            <el-form-item label="密码" prop="password">
              <el-input 
                v-model="loginForm.password" 
                type="password" 
                prefix-icon="Lock" 
                placeholder="请输入管理员密码" 
                show-password
                size="large"
>
              </el-input>
            </el-form-item>
            
            <el-form-item>
              <el-button 
                type="danger" 
                size="large"
                style="width: 100%" 
                :loading="authStore.loading" 
                @click="submitForm"
>
                <el-icon><Key /></el-icon>
                管理员登录
              </el-button>
            </el-form-item>
            
            <el-form-item>
              <router-link to="/register" style="width: 100%; display: block;">
                <el-button type="primary" size="large" style="width: 100%;">
                  注册管理员账号
                </el-button>
              </router-link>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
      
      <div class="form-footer">
        <span>系统功能说明：游客可浏览赛事信息，管理员可进行数据管理</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { User, Key, Right } from '@element-plus/icons-vue'
import { useLoginPage } from '@/composables/auth'

const { 
  authStore,
  loginFormRef,
  activeTab,
  guestLoading,
  loginForm,
  rules,
  guestLogin,
  submitForm,
  handleTabChange
} = useLoginPage()
</script>

<style scoped>
.login-container {
  height: 100vh;
  background: linear-gradient(135deg, #8BC6EC 0%, #9599E2 100%);
  display: flex;
  justify-content: center;
  align-items: center;
}

.auth-container {
  background: rgba(255, 255, 255, 0.95);
  padding: 40px;
  border-radius: 15px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
  width: 450px;
  backdrop-filter: blur(10px);
  animation: fadeIn 0.5s ease;
}

.auth-title {
  text-align: center;
  color: #2d3748;
  margin-bottom: 30px;
  font-size: 24px;
  font-weight: 600;
}

.login-tabs {
  margin-bottom: 20px;
}

.guest-content {
  text-align: center;
  padding: 20px 0;
}

.guest-icon {
  color: #409eff;
  margin-bottom: 20px;
}

.guest-description {
  color: #606266;
  margin-bottom: 30px;
  font-size: 14px;
  line-height: 1.5;
}

.form-footer {
  text-align: center;
  margin-top: 20px;
  color: #909399;
  font-size: 12px;
  line-height: 1.4;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

:deep(.el-tabs__header) {
  margin-bottom: 20px;
}

:deep(.el-tabs__item) {
  font-weight: 500;
  color: #606266;
}

:deep(.el-tabs__item.is-active) {
  color: #409eff;
  font-weight: 600;
}

:deep(.el-form-item__label) {
  color: #2d3748;
  font-weight: 500;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

:deep(.el-button--primary) {
  border-radius: 8px;
  font-weight: 600;
}

:deep(.el-button--danger) {
  border-radius: 8px;
  font-weight: 600;
  background: linear-gradient(45deg, #f56565, #ed8936);
  border: none;
}
</style>