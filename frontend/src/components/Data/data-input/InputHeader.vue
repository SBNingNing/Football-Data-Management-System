<template>
  <div class="page-header">
    <div class="header-content">
      <div class="header-main">
        <h2 class="page-title">
          <el-icon class="title-icon"><EditPen /></el-icon>
          信息录入管理
        </h2>
        <p class="page-description">请先选择赛事类型，然后选择要录入的信息类型进行操作</p>
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
defineEmits(['refresh', 'scroll-top'])
import { EditPen, Refresh, ArrowUp } from '@element-plus/icons-vue'
</script>
<!-- 样式已合并至 admin-management.css，全局复用 .page-header 等类 -->
