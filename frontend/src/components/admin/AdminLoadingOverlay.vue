<template>
  <div v-if="loading" class="loading-overlay">
    <div class="loading-content">
      <el-icon class="loading-icon is-loading"><Loading /></el-icon>
      <p class="loading-text">正在加载数据...</p>
    </div>
  </div>
</template>
<script setup>
import { Loading } from '@element-plus/icons-vue'
defineProps({ loading: Boolean })
</script>
