import { createRouter, createWebHistory } from 'vue-router'
import Home from '../pages/Home.vue'
import UsersSearch from '../pages/UsersSearch.vue'
import UserProfile from '../pages/UserProfile.vue'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/users', name: 'Users', component: UsersSearch },
  { path: '/users/:id', name: 'UserProfile', component: UserProfile},
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
