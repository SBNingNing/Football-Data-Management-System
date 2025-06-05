import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/auth/Login.vue'
import Register from '../views/auth/Register.vue'
import Home from '../views/Home.vue'
import Board from '../views/admin/board.vue'
import PlayerHistory from '../views/player/player_history.vue'
import TeamHistory from '../views/team/team_history.vue'
import TournamentHistory from '../views/tournament/tournament_history.vue'

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
    path: '/team',
    name: 'TeamHistory',
    component: TeamHistory
  },
  {
    path: '/tournament',
    name: 'TournamentHistory',
    component: TournamentHistory
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router