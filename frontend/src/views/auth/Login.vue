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
import '@/assets/styles/auth-pages.css'

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
/* Login页面特有样式已移至 @/assets/styles/auth-pages.css */
</style>