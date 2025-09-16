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
import '@/styles/global.css'

const app = createApp(App)

const pinia = createPinia()
app.use(pinia)
app.use(router)
app.use(ElementPlus)

// 恢复 token -> axios header
const authStore = useAuthStore()
authStore.init()

app.mount('#app')
