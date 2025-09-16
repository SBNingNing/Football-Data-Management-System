<template>
  <div v-if="visible" class="error-banner" :class="{ 'is-dense': dense }">
    <el-icon class="icon" color="#f56c6c"><WarningFilled /></el-icon>
    <div class="message">{{ displayMessage }}</div>
    <div class="actions">
      <el-button v-if="retry" size="small" type="primary" plain @click="onRetry">重试</el-button>
      <slot name="extra" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { normalizeError } from '@/utils/error'
import { WarningFilled } from '@element-plus/icons-vue'

const props = defineProps({
  error: { type: [Object, String], default: null },
  retry: { type: Function, default: null },
  dense: { type: Boolean, default: false },
  fallback: { type: String, default: '加载失败' }
})

const emit = defineEmits(['retry'])

const norm = computed(() => {
  if (!props.error) return null
  if (typeof props.error === 'string') return { message: props.error }
  return normalizeError(props.error)
})

const displayMessage = computed(() => norm.value?.message || props.fallback)
const visible = computed(() => !!norm.value)

function onRetry() {
  if (props.retry) props.retry()
  emit('retry')
}
</script>

<style scoped>
.error-banner { display:flex; align-items:center; padding:10px 12px; border:1px solid #fbc4c4; background:#fef0f0; border-radius:6px; gap:8px; }
.error-banner.is-dense { padding:6px 8px; }
.icon { flex-shrink:0; }
.message { flex:1; font-size:13px; color:#c45656; line-height:1.4; }
.actions { display:flex; align-items:center; gap:6px; }
</style>
