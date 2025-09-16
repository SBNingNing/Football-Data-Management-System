<template>
  <div class="panel-skeleton" :class="{ card }">
    <div v-for="n in rows" :key="n" class="sk-row">
      <div v-if="avatar" class="sk-avatar" />
      <div class="sk-lines">
        <el-skeleton :rows="1" animated :throttle="80" />
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  rows: { type: Number, default: 3 },
  avatar: { type: Boolean, default: false },
  card: { type: Boolean, default: true }
})
</script>

<style scoped>
.panel-skeleton { width:100%; }
.panel-skeleton.card { padding:12px 14px; background:#fff; border:1px solid var(--el-border-color-light); border-radius:8px; }
.sk-row { display:flex; align-items:center; gap:12px; padding:4px 0; }
.sk-avatar { width:36px; height:36px; border-radius:50%; background:var(--el-color-info-light-7,#ebeef5); }
.sk-lines { flex:1; }
</style>
