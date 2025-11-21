<template>
  <div class="search-section">
    <el-row :gutter="20" align="middle" class="search-row">
      <slot></slot>
    </el-row>
  </div>
</template>

<script setup>
// 搜索区域容器组件，用于统一管理搜索区域的样式和布局
</script>

<style scoped>
.search-section {
  margin-bottom: 20px;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.search-row {
  margin-bottom: 0 !important;
}
</style>