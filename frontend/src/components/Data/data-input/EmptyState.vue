<template>
  <div class="empty-state">
    <el-empty description="请先选择比赛类型开始录入" :image-size="160">
      <template #image>
        <div class="empty-icon">
          <el-icon size="160" color="#d1d5db"><Box /></el-icon>
        </div>
      </template>
    </el-empty>
  </div>
</template>
<script setup>
import { Box } from '@element-plus/icons-vue'
</script>
<style scoped>
.empty-state { }
</style>
