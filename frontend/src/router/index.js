import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/auth/Login.vue'
import Register from '../views/auth/Register.vue'
import Home from '../views/Home.vue'
import Board from '../views/admin/board.vue'
import PlayerHistory from '../views/player/player_history.vue'
import TeamHistory from '../views/team/team_history.vue'
import TournamentHistory from '../views/tournament/tournament_history.vue'
import MatchDetail from '../views/match/match_detail.vue'

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
    component: Home
  },
  {
    path: '/admin/board',
    name: 'Board',
    component: Board
  },
  {
    path: '/player',
    name: 'PlayerHistory',
    component: PlayerHistory
  },
  {
    path: '/player/:playerId',
    name: 'PlayerDetail',
    component: PlayerHistory,
    props: route => ({ 
      playerId: route.params.playerId,
      ...route.query
    })
  },
  {
    path: '/team',
    name: 'TeamHistory',
    component: TeamHistory
  },
  {
    path: '/tournament',
    redirect: '/home'
  },
  {
    path: '/tournament/:tournamentName',
    name: 'TournamentHistory',
    component: TournamentHistory
  },
  {
    path: '/match-detail/:matchId',
    name: 'match-detail',
    component: MatchDetail,
    props: route => ({
      matchId: route.params.matchId,
      ...route.query
    })
  },
  {
    path: '/match/detail/:matchId',
    name: 'match-detail-alt',
    component: MatchDetail,
    props: route => ({
      matchId: route.params.matchId,
      ...route.query
    })
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router