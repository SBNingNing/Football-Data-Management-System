<template>
  <div class="stat-card" :class="variantClass">
    <div class="stat-card__value">{{ value }}</div>
    <div class="stat-card__label">{{ label }}</div>
  </div>
</template>

<script setup>
/**
 * 通用统计卡片组件
 * Props:
 *  - value: 数值/展示主信息
 *  - label: 标题文本
 *  - type: goals|yellow|red (决定配色) 可扩展
 */
import { computed } from 'vue'
const props = defineProps({
  value: { type: [String, Number], default: 0 },
  label: { type: String, default: '' },
  type: { type: String, default: 'goals' }
})

const variantClass = computed(() => {
  switch (props.type) {
    case 'yellow': return 'stat-card--yellow'
    case 'red': return 'stat-card--red'
    case 'goals':
    default: return 'stat-card--goals'
  }
})
</script>

<style scoped>
.stat-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md, 8px);
  min-height: 100px;
  transition: transform .2s ease;
  box-shadow: var(--shadow-card, 0 2px 8px rgba(0,0,0,.08));
  text-align: center;
}
.stat-card:hover { transform: translateY(-2px); }
.stat-card__value { font-size: 28px; font-weight: 700; line-height: 1; }
.stat-card__label { margin-top: 6px; font-size: 14px; opacity: .9; }
</style>
