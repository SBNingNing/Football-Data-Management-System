<template>
  <div class="error-boundary" v-if="hasError">
    <el-alert
      :title="errorTitle"
      type="error"
      :description="errorDescription"
      show-icon
      :closable="false"
    />
    <div class="error-actions">
      <el-button @click="retry" type="primary">重试</el-button>
      <el-button @click="reload" type="default">刷新页面</el-button>
    </div>
  </div>
  <div v-else>
    <slot></slot>
  </div>
</template>

<script setup>
import { ref, computed, onErrorCaptured, nextTick } from 'vue'

const hasError = ref(false)
const error = ref(null)
const errorInfo = ref(null)

const errorTitle = computed(() => error.value?.name || '组件错误')
const errorDescription = computed(() => error.value?.message || '组件渲染时发生错误，请重试或刷新页面')

onErrorCaptured((err, instance, info) => {
  console.error('ErrorBoundary captured error:', err, info)
  hasError.value = true
  error.value = err
  errorInfo.value = info
  return false
})

const retry = () => {
  hasError.value = false
  error.value = null
  errorInfo.value = null
  nextTick(() => {
    // 简单的重置状态通常足以让Vue重新尝试渲染插槽内容
  })
}

const reload = () => {
  window.location.reload()
}
</script>

<style scoped>
.error-boundary {
  padding: 20px;
}

.error-actions {
  margin-top: 16px;
  display: flex;
  gap: 8px;
}
</style>
