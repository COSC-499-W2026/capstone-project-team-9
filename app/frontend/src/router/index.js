import { createRouter, createWebHistory } from 'vue-router'
import PlayView from '../views/PlayView.vue'

const routes = [
  { path: '/', name: 'play', component: PlayView },
  // add new screens here, e.g.
  // { path: '/login', name: 'login', component: () => import('../views/LoginView.vue') },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})