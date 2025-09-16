// notify.js: 统一通知封装 (Element Plus ElMessage / 未来可替换)
// 用法: import notify from '@/utils/notify'; notify.success('创建成功')
import { ElMessage } from 'element-plus'

function base(type, message, opts={}){
  if(!message) return
  ElMessage({ type, message, showClose: true, duration: 2500, ...opts })
}

const notify = {
  success: (msg, opts) => base('success', msg, opts),
  error: (msg, opts) => base('error', msg, opts),
  warning: (msg, opts) => base('warning', msg, opts),
  info: (msg, opts) => base('info', msg, opts)
}

export default notify
