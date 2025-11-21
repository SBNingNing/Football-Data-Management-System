// auth.js: 认证相关接口封装 -> 对应后端 /api/auth/*
import http from '@/utils/httpClient';
import { setAuthToken } from '@/utils/httpClient';
import logger from '@/utils/logger';

// POST /auth/login 登录，返回 token + user
export async function login(credentials) {
  const r = await http.post('/auth/login', credentials);
  const { access_token, user } = r.data;
  setAuthToken(access_token);
  return { token: access_token, user };
}

// POST /auth/register 注册
export async function register(userData) { return http.post('/auth/register', userData); }

// POST /auth/register-admin 管理员注册
export async function registerAdmin(adminData) {
  return http.post('/auth/register-admin', adminData);
}

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
  
  // 检查请求是否成功
  if (!r.ok) {
    // 如果请求失败，抛出包含后端错误信息的错误
    throw new Error(r.error?.message || '登录请求失败');
  }
  
  const { access_token, user } = r.data;
  setAuthToken(access_token);
  // 使用后端返回的真实角色，而不是硬编码
  return { token: access_token, user: user };
}

// GET /auth/me 获取当前登录用户
export async function getMe() {
  try {
    // 确保 token 存在
    const token = localStorage.getItem('token');
    if (!token) {
      throw new Error('No authentication token found');
    }
    
    const r = await http.get('/auth/me', {
      retry: {
        times: 1,
        delay: () => 500
      }
    });
    
    if (!r.ok) {
      throw new Error(r.error?.message || 'Failed to fetch user info');
    }
    
    return r.data; // 直接返回 user 视图结构
  } catch (error) {
    logger.error('getMe 失败:', error);
    // 清除无效 token
    if (error.status === 401) {
      setAuthToken(null);
    }
    throw error;
  }
}

// 清除认证头
export function logout() { setAuthToken(null); }