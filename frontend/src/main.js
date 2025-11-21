import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import { useAuthStore } from '@/store/modules'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './assets/main.css'
import '@/assets/styles/variables.css'
import '@/assets/styles/base.css'
import '@/assets/styles/admin-management.css'
import extensionCompatibility from '@/utils/extensionCompatibility'

// 初始化浏览器扩展兼容性保护
extensionCompatibility.init()

const app = createApp(App)

// 全局错误处理
app.config.errorHandler = (error, instance, info) => {
  // 过滤扩展相关错误
  if (error.message && (
    error.message.includes('runtime.lastError') ||
    error.message.includes('message port closed') ||
    error.message.includes('Extension context')
  )) {
    console.warn('Vue应用中检测到扩展错误，已忽略:', error.message)
    return
  }
  
  console.error('Vue应用错误:', error, info)
  // 不要阻止错误冒泡，以便其他错误处理器可以处理
}

// 处理Promise未捕获的异常
window.addEventListener('unhandledrejection', (event) => {
  const reason = event.reason
  
  // 过滤扩展相关的Promise拒绝
  if (reason && (
    reason.message?.includes('runtime.lastError') ||
    reason.message?.includes('message port closed') ||
    reason.message?.includes('Extension context')
  )) {
    console.warn('检测到扩展相关的Promise拒绝，已忽略:', reason.message)
    event.preventDefault()
    return
  }
  
  console.warn('未捕获的Promise异常:', reason)
  // 可以选择阻止错误冒泡到控制台
  // event.preventDefault()
})

// 处理运行时错误
window.addEventListener('error', (event) => {
  const message = event.message || ''
  
  // 过滤扩展相关错误
  if (
    message.includes('runtime.lastError') ||
    message.includes('message port closed') ||
    message.includes('Extension context')
  ) {
    console.warn('检测到扩展相关的运行时错误，已忽略:', message)
    event.preventDefault()
    return
  }
  
  console.error('运行时错误:', event.error)
})

const pinia = createPinia()
app.use(pinia)
app.use(router)
app.use(ElementPlus)

// 恢复 token -> axios header
const authStore = useAuthStore()
authStore.init()
// 刷新当前用户，确保角色一致（在页面刷新或首次进入时）
authStore.fetchMe?.()

app.mount('#app')