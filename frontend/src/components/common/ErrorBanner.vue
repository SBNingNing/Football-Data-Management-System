<template>
  <div v-if="visible" class="error-banner float-shadow" :class="{ 'is-dense': dense }">
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
import '@/assets/styles/error-banner.css'

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