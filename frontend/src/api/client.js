// axios 单例：统一配置 baseURL('/api')、超时、Auth 头；供各业务 api 模块复用。
// 后端所有 REST 资源（/auth /teams /players /matches /events ...）都通过此实例发起。
import axios from 'axios';

const client = axios.create({ baseURL: '/api', timeout: 15000 });

// 设置/清除认证头 (登录/登出/恢复会话)
export function setAuthToken(token) {
  if (token) {
    client.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    localStorage.setItem('token', token);
  } else {
    delete client.defaults.headers.common['Authorization'];
    localStorage.removeItem('token');
  }
}

// 简单响应拦截，可根据需要扩展
client.interceptors.response.use(
  r => r,
  err => {
    const status = err?.response?.status;
    const payload = err?.response?.data;
    const message = payload?.message || payload?.error || err.message || '请求失败';
    const normalized = { isApiError: true, statusCode: status, message, raw: err };
    return Promise.reject(normalized);
  }
);

export default client;
