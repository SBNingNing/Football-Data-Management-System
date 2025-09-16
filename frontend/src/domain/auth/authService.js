// authService: 登录 / 游客登录 / 当前用户
import http from '@/utils/httpClient'
import { serviceWrap, buildError } from '@/utils/error'

export function login({ username, password }) {
  return serviceWrap(async () => {
    if(!username || !password) throw buildError('缺少用户名或密码', 'AUTH_CREDENTIALS_MISSING')
    const res = await http.post('/auth/login', { username, password })
    if(!res.ok) throw buildError(res.error?.message || '登录失败', 'AUTH_LOGIN_FAILED', res.error)
    return res.data
  })
}

export function guestLogin(){
  return serviceWrap(async () => {
    const res = await http.post('/auth/guest-login')
    if(!res.ok) throw buildError(res.error?.message || '游客登录失败', 'AUTH_GUEST_FAILED', res.error)
    return res.data
  })
}

export function fetchMe(){
  return serviceWrap(async () => {
    const res = await http.get('/auth/me')
    if(!res.ok) throw buildError(res.error?.message || '获取当前用户失败', 'AUTH_ME_FAILED', res.error)
    return res.data
  })
}

export function register({ username, password, email }) {
  return serviceWrap(async () => {
    if(!username || !password || !email) throw buildError('缺少注册必填字段', 'AUTH_REGISTER_MISSING_FIELDS')
    const res = await http.post('/auth/register', { username, password, email })
    if(!res.ok) throw buildError(res.error?.message || '注册失败', 'AUTH_REGISTER_FAILED', res.error)
    return res.data
  })
}
