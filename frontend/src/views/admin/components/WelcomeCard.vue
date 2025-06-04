<template>
  <el-card class="welcome-card">
    <div slot="header" class="clearfix">
      <span>足球管理系统管理员界面</span>
      <div style="float: right;">
        <el-button type="text" @click="$emit('go-to-home')">查看前台</el-button>
        <el-button type="text" @click="$emit('logout')">退出登录</el-button>
      </div>
    </div>
    <p>欢迎管理员，您可以通过以下功能管理比赛信息。</p>
  </el-card>
</template>

<script>
export default {
  name: 'WelcomeCard'
}
</script>

<style scoped>
.welcome-card {
  margin-bottom: 20px;
}
</style>
