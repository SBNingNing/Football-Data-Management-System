<template>
  <div class="register-container">
    <div class="auth-container card-wrapper">
      <h2 class="auth-title">用户注册</h2>
      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="rules"
        label-position="top"
        @submit.prevent="submitForm"
        class="register-form"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="registerForm.username" placeholder="请输入用户名" clearable />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="registerForm.email" placeholder="请输入邮箱" clearable />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="registerForm.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="registerForm.confirmPassword" type="password" placeholder="请再次输入密码" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" style="width:100%" :loading="authStore.loading" @click="submitForm">注册</el-button>
        </el-form-item>
        <div class="form-footer">
          <span>已有账号？</span>
          <router-link to="/login">返回登录</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
/*
 * Unified Register Component
 * 合并自原 `Register.vue` 与 `Register_new.vue`
 * 变更要点:
 * 1. 采用新版 UI 布局与渐变背景
 * 2. 保留并使用组合式 `useRegisterPage` 的 store 提交逻辑
 * 3. 去除旧文件内手动 redirect 函数, 改用 router-link
 * 4. 删除旧的局部 data(`submitting`), 使用 authStore.loading
 */
import { useRegisterPage } from '@/composables/auth'
const { authStore, registerFormRef, registerForm, rules, submitForm } = useRegisterPage()
</script>

<style scoped>
.register-container { height:100vh; background:linear-gradient(135deg,#8BC6EC 0%,#9599E2 100%); display:flex; justify-content:center; align-items:center; padding:24px; box-sizing:border-box; }
.card-wrapper { width:400px; background:#fff; border-radius:16px; padding:40px 42px 32px; box-shadow:0 10px 28px rgba(0,0,0,.12); }
.auth-title { margin:0 0 28px; font-size:24px; font-weight:600; text-align:center; color:#303133; letter-spacing:.5px; }
.register-form :deep(.el-form-item) { margin-bottom:18px; }
.form-footer { display:flex; justify-content:center; gap:6px; font-size:14px; color:#606266; margin-top:4px; }
.form-footer a { color: var(--el-color-primary); text-decoration:none; }
.form-footer a:hover { text-decoration:underline; }
@media (max-width:520px){
  .card-wrapper { width:100%; padding:32px 28px 28px; }
  .auth-title { font-size:22px; }
}
</style>


