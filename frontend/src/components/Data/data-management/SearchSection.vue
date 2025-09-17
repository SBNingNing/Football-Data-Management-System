<template>
  <div class="search-section">
    <el-row :gutter="gutter">
      <slot />
    </el-row>
  </div>
</template>
<script setup>
/**
 * SearchSection 通用搜索行容器
 * Props:
 *  - gutter: 行间距 (默认 15)
 * Slot: 默认插入 <el-col> 子元素
 */
const { gutter } = defineProps({ gutter: { type: Number, default: 15 } })
</script>
<style scoped>
/* 如果后续需要局部定制，可在此添加；目前主要样式在全局 management.css */
</style>
