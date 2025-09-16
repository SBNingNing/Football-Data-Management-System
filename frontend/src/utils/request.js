import axios from 'axios'
import { ElMessage } from 'element-plus'
import logger from '@/utils/logger'

// 创建axios实例
const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api', // 使用 Vite 的环境变量
  timeout: 15000 // 请求超时时间
})

// 请求拦截器
service.interceptors.request.use(
  config => {
  logger.debug('[request] 发送', config.method?.toUpperCase(), config.url)
  logger.debug('[request] 配置', config)
    
    // 如果有token，添加到请求头
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
  logger.error('[request] 请求拦截器错误', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
  logger.debug('[request] 响应', response.status)
    return response
  },
  error => {
  logger.error('[request] 响应错误', error)
    
    if (error.code === 'ECONNABORTED') {
      ElMessage.error('请求超时，请检查网络连接')
    } else if (error.message.includes('Network Error')) {
      ElMessage.error('网络连接失败，请检查后端服务是否启动')
    } else if (error.response) {
      const { status, data } = error.response
      ElMessage.error(`服务器错误 (${status}): ${data?.message || '未知错误'}`)
    } else {
      ElMessage.error('请求失败，请稍后重试')
    }
    
    return Promise.reject(error)
  }
)

export default service
