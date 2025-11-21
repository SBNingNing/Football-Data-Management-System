<template>
  <div class="panel-skeleton" :class="{ card: card, 'card-hover': card }">
    <div v-for="n in rows" :key="n" class="sk-row">
      <div v-if="avatar" class="sk-avatar btn-hover" />
      <div class="sk-lines">
        <el-skeleton :rows="1" animated :throttle="80" />
      </div>
    </div>
  </div>
</template>

<script setup>
import '@/assets/styles/panel-skeleton.css'

defineProps({
  rows: { type: Number, default: 3 },
  avatar: { type: Boolean, default: false },
  card: { type: Boolean, default: true }
})
</script>