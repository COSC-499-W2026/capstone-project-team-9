import { createRouter, createWebHistory } from 'vue-router'
import PlayView from '../views/PlayView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import LandingView from '../views/LandingView.vue'
import ClueView from '../views/ClueView.vue'
import CourseView from '@/views/CourseView.vue'
import CourseListView from '@/views/CourseListView.vue'

const routes = [
  { path: '/', name: 'landing', component: LandingView },
  { path: '/play', name: 'play', component: PlayView },
  { path: '/play/:playId', name: 'clue', component: ClueView, props: true },
  { path: '/login', name: 'login', component: LoginView },
  { path: '/register', name: 'register', component: RegisterView },
  { path: '/courses', name: 'courses', component: CourseView },
  { path: '/courses/:courseId', name: 'course', component: CourseListView, props: true },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})