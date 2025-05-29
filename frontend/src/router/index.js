import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../store/modules/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/auth/LoginView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/dashboard/DashboardView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/players',
    name: 'Players',
    component: () => import('../views/player/PlayerListView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/players/add',
    name: 'AddPlayer',
    component: () => import('../views/player/PlayerFormView.vue'),
    meta: { requiresAuth: true, roles: ['ADMIN', 'RECORDER'] }
  },
  {
    path: '/players/:id/edit',
    name: 'EditPlayer',
    component: () => import('../views/player/PlayerFormView.vue'),
    meta: { requiresAuth: true, roles: ['ADMIN', 'RECORDER'] }
  },
  {
    path: '/teams',
    name: 'Teams',
    component: () => import('../views/team/TeamListView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/matches',
    name: 'Matches',
    component: () => import('../views/match/MatchListView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/tournaments',
    name: 'Tournaments',
    component: () => import('../views/tournament/TournamentListView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/seasons',
    name: 'Seasons',
    component: () => import('../views/season/SeasonListView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/statistics',
    name: 'Statistics',
    component: () => import('../views/statistics/StatisticsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/common/NotFoundView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  if (to.meta.requiresAuth && !userStore.isAuthenticated) {
    next({ name: 'Login' })
  } else if (to.meta.roles && !to.meta.roles.includes(userStore.userRole)) {
    next({ name: 'Dashboard' })
  } else {
    next()
  }
})

export default router
