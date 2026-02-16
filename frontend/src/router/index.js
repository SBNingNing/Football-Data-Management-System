import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/auth/Login.vue'
import Register from '../views/auth/Register.vue'
import Home from '../views/Home.vue'
import Board from '../views/admin/board.vue'
import PlayerHistory from '../views/player/player_history.vue'
import TeamHistory from '../views/team/team_history.vue'
import TournamentHistory from '../views/tournament/tournament_history.vue'
import MatchDetail from '../views/match/match_detail.vue'
import { useAuthGuard } from '@/composables/auth'
import { useAuthStore } from '@/store/modules/auth'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/register',
    name: 'AdminRegister', 
    component: Register,
    meta: { 
      title: '管理员注册',
      // 对应后端 /auth/register-admin 接口
      // 此页面为公开注册页面，用于创建初始管理员
    }
  },
  {
    path: '/home',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin/board',
    name: 'Board',
    component: Board,
    meta: { requiresAuth: true, roles: ['admin'] }
  },
  {
    path: '/player',
    name: 'PlayerHistory',
    component: PlayerHistory,
    meta: { requiresAuth: true }
  },
  {
    path: '/player/:playerId',
    name: 'PlayerDetail',
    component: PlayerHistory,
    props: route => ({ 
      playerId: route.params.playerId,
      ...route.query
    }),
    meta: { requiresAuth: true }
  },
  {
    path: '/team',
    name: 'TeamHistory',
    component: TeamHistory,
    meta: { requiresAuth: true }
  },
  {
    path: '/team/:teamName',
    name: 'TeamInfo',
    component: TeamHistory,
    props: route => ({
      teamName: route.params.teamName,
      ...route.query
    }),
    meta: { requiresAuth: true }
  },
  {
    path: '/tournament',
    name: 'Tournament',
    component: () => import('../views/tournament/index.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/tournament/:tournamentName',
    name: 'TournamentHistory',
    component: TournamentHistory,
    meta: { requiresAuth: true }
  },
  {
    path: '/match-detail/:matchId',
    name: 'match-detail',
    component: MatchDetail,
    props: route => ({
      matchId: route.params.matchId,
      ...route.query
    }),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局前置守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // 页面刷新时，如果存在token但没有用户信息，尝试获取用户信息
  if (authStore.token && !authStore.user) {
    try {
      await authStore.fetchMe()
    } catch (error) {
      console.error('路由守卫获取用户信息失败:', error)
    }
  }

  const { check } = useAuthGuard()
  const r = check(to)
  if (r.allow) return next()
  if (r.redirect) {
    return next({ path: r.redirect, query: { redirect: to.fullPath, reason: r.reason } })
  }
  next(false)
})

export default router