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
    name: 'Register',
    component: Register
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
    redirect: '/home'
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
  },
  {
    path: '/match/detail/:matchId',
    name: 'match-detail-alt',
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
router.beforeEach((to, from, next) => {
  const { check } = useAuthGuard()
  const r = check(to)
  if (r.allow) return next()
  if (r.redirect) {
    return next({ path: r.redirect, query: { redirect: to.fullPath, reason: r.reason } })
  }
  next(false)
})

export default router