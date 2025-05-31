<template>
  <div class="login-container">
    <div class="auth-container">
      <h2 class="auth-title">科大校园足球赛事管理系统</h2>
      <el-form :model="loginForm" :rules="rules" ref="loginFormRef" label-position="top" @submit.prevent="submitForm">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="loginForm.username" prefix-icon="el-icon-user" placeholder="请输入用户名"></el-input>
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input v-model="loginForm.password" type="password" prefix-icon="el-icon-lock" placeholder="请输入密码" show-password></el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" style="width: 100%" :loading="userStore.loading" @click="submitForm">登录</el-button>
        </el-form-item>
        
        <div class="form-footer">
          <span>没有账号？</span>
          <router-link to="/register">立即注册</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const loginFormRef = ref(null)

const loginForm = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const submitForm = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      const success = await userStore.login(loginForm)
      
      if (success) {
        ElMessage.success('登录成功')
        router.push('/home')
      } else {
        ElMessage.error(userStore.error || '登录失败')
      }
    }
  })
}
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
  animation: fadeIn 0.5s ease;
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
</style>
