<template>
  <div class="home-container">
    <el-container>
      <el-header>
        <div class="header-content">
          <h2>科大校园足球赛事管理系统</h2>
          <div class="user-info">
            <span>{{ userStore.currentUser?.username }}</span>
            <el-button type="text" @click="handleLogout">退出</el-button>
          </div>
        </div>
      </el-header>
      
      <el-main>
        <div class="welcome-container">
          <h1>欢迎使用科大校园足球赛事管理系统</h1>
          <p>这是一个测试主页，登录成功！</p>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { useUserStore } from '@/store'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()
const router = useRouter()

const handleLogout = () => {
  userStore.logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>

<style scoped>
.home-container {
  min-height: 100vh;
}

.el-header {
  background-color: #409EFF;
  color: white;
  line-height: 60px;
  padding: 0 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.el-main {
  padding: 20px;
}

.welcome-container {
  text-align: center;
  margin-top: 100px;
}

.welcome-container h1 {
  font-size: 32px;
  color: #303133;
  margin-bottom: 20px;
}

.welcome-container p {
  font-size: 18px;
  color: #606266;
}
</style>
