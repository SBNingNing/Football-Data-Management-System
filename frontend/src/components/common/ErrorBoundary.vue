<!-- ErrorBoundary.vue - 错误边界组件 -->
<template>
  <div v-if="hasError" class="error-boundary">
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
  <slot v-else></slot>
</template>

<script>
export default {
  name: 'ErrorBoundary',
  data() {
    return {
      hasError: false,
      error: null,
      errorInfo: null
    }
  },
  computed: {
    errorTitle() {
      return this.error?.name || '组件错误'
    },
    errorDescription() {
      return this.error?.message || '组件渲染时发生错误，请重试或刷新页面'
    }
  },
  errorCaptured(error, instance, info) {
    console.error('ErrorBoundary captured error:', error, info)
    this.hasError = true
    this.error = error
    this.errorInfo = info
    
    // 阻止错误继续冒泡
    return false
  },
  methods: {
    retry() {
      this.hasError = false
      this.error = null
      this.errorInfo = null
      this.$nextTick(() => {
        // 强制重新渲染子组件
        this.$forceUpdate()
      })
    },
    reload() {
      window.location.reload()
    }
  }
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