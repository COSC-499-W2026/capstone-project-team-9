import { createRouter, createWebHistory } from 'vue-router'
import PlayView from '../views/PlayView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import LandingView from '../views/LandingView.vue'
import ClueView from '../views/ClueView.vue'
import CourseListView from '../views/CourseListView.vue'
import CourseDetailView from '../views/CourseDetailView.vue'
import { blockGuests } from './guards'

const routes = [
  { path: '/', name: 'landing', component: LandingView },
  { path: '/play', name: 'play', component: PlayView },
  { path: '/play/:playId', name: 'clue', component: ClueView, props: true },
  { path: '/login', name: 'login', component: LoginView },
  { path: '/register', name: 'register', component: RegisterView },
  { path: '/courses', name: 'courses', component: CourseListView, meta: { noGuests: true } },
  { path: '/courses/:courseId', name: 'course', component: CourseDetailView, props: true, meta: { noGuests: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(blockGuests)

export default router