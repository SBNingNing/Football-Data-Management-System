<template>
  <div class="register-container">
    <div class="auth-container">
      <h2 class="auth-title">管理员注册</h2>
      <div class="admin-notice">
        <el-icon class="notice-icon"><InfoFilled /></el-icon>
        <span>此界面仅用于创建系统管理员账号</span>
      </div>
      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="rules"
        label-position="top"
        @submit.prevent="submitForm"
        class="register-form"
      >
        <el-form-item label="管理员用户名" prop="username">
          <el-input v-model="registerForm.username" placeholder="请输入管理员用户名" clearable />
        </el-form-item>
        <el-form-item label="管理员邮箱" prop="email">
          <el-input v-model="registerForm.email" placeholder="请输入管理员邮箱" clearable />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="registerForm.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="registerForm.confirmPassword" type="password" placeholder="请再次输入密码" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" style="width:100%" :loading="authStore.loading" @click="submitForm">
            <el-icon><UserFilled /></el-icon>
            创建管理员账号
          </el-button>
        </el-form-item>
        <div class="form-footer">
          <span>已有管理员账号？</span>
          <router-link to="/login">返回登录</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
/*
 * Admin Registration Component
 * 管理员注册组件 - 从普通用户注册改造而来
 * 
 * 功能特点:
 * 1. 直接创建管理员账号，无需额外PowerShell提权操作
 * 2. 界面风格与登录页面保持一致
 * 3. 预留游客/管理员权限分离的扩展结构
 * 
 * 后续扩展预留:
 * - 游客登录状态判断逻辑
 * - 界面权限控制入口
 * - 游客仅显示游客界面的权限过滤
 */
import { InfoFilled, UserFilled } from '@element-plus/icons-vue'
import { useAdminRegisterPage } from '@/composables/auth'
import '@/assets/styles/auth-pages.css'
const { authStore, registerFormRef, registerForm, rules, submitForm } = useAdminRegisterPage()
</script>

<style scoped>
/* Register页面特有样式已移至 @/assets/styles/auth-pages.css */
</style>