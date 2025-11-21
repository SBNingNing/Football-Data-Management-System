<template>
  <div class="tournaments-page">
    <div class="page-header">
      <h1>校园足球活动管理</h1>
      <p class="page-description">管理学期活动和校园足球活动</p>
    </div>
    
    <MetaDataSection />
  </div>
</template>

<script setup>
import MetaDataSection from '@/components/common/MetaDataSection.vue'
</script>

<style scoped>
.tournaments-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-header h1 {
  color: #1f2937;
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 8px;
}

.page-description {
  color: #6b7280;
  font-size: 16px;
}
</style>