<template>
  <div class="home-container">
    <el-card>
      <div slot="header">
        <h2>足球管理系统</h2>
      </div>
      <div class="welcome-message">
        <h3>欢迎您，{{ username }}!</h3>
        <p>这是一个空的测试页面</p>
      </div>
      <el-button type="danger" @click="logout">退出登录</el-button>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'Home',
  data() {
    return {
      username: localStorage.getItem('username') || '用户'
    }
  },
  methods: {
    logout() {
      // 清除存储的信息
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      this.$message.success('已退出登录')
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.home-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}
.welcome-message {
  margin: 20px 0;
}
</style>
