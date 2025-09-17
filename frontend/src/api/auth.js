// auth.js: 认证相关接口封装 -> 对应后端 /api/auth/*
import http from '@/utils/httpClient';
import { setAuthToken } from '@/utils/httpClient';

// POST /auth/login 登录，返回 token + user
export async function login(credentials) {
  const r = await http.post('/auth/login', credentials);
  const { access_token, user } = r.data;
  setAuthToken(access_token);
  return { token: access_token, user };
}

// POST /auth/register 注册
export async function register(userData) { return http.post('/auth/register', userData); }

// POST /auth/guest-login 游客登录
export async function guestLogin() {
  const r = await http.post('/auth/guest-login');
  const { access_token } = r.data;
  setAuthToken(access_token);
  return { token: access_token };
}

// POST /auth/login 但前端额外标记 role=admin
export async function adminLogin(credentials) {
  const r = await http.post('/auth/login', credentials);
  const { access_token, user } = r.data;
  setAuthToken(access_token);
  return { token: access_token, user: { ...user, role: 'admin' } };
}

// 清除认证头
export function logout() { setAuthToken(null); }