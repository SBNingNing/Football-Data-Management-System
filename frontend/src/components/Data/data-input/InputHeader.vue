<template>
  <div class="page-header">
    <div class="header-content">
      <div class="header-main">
        <h2 class="page-title">
          <el-icon class="title-icon"><EditPen /></el-icon>
          信息录入管理
        </h2>
        <p class="page-description">请先选择比赛类型，然后选择要录入的信息类型进行操作</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" class="refresh-button" @click="$emit('refresh')">
          <el-icon><Refresh /></el-icon>
          刷新数据
        </el-button>
        <el-button text @click="$emit('scroll-top')">
          <el-icon><ArrowUp /></el-icon>
          回到顶部
        </el-button>
      </div>
    </div>
  </div>
</template>
<script setup>
import { EditPen, Refresh, ArrowUp } from '@element-plus/icons-vue'
</script>
<style scoped>
.page-header { margin-bottom: 32px; padding: 32px 0; }
.header-content { display:flex; justify-content:space-between; align-items:flex-start; gap:24px; min-height:80px; }
.header-actions { display:flex; gap:12px; flex-shrink:0; align-items:flex-start; padding-top:8px; }
.refresh-button { min-width:120px; white-space:nowrap; font-weight:600; }
</style>
