import Vue from 'vue'
import VueRouter from 'vue-router'

Vue.use(VueRouter)

const routers = [
  {
    path: '/',
    component: () => import('@/views/index.vue')
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('../views/Register.vue')
  },
  {
    path: '/detail',
    name: 'detail',
    component: () => import('../views/Detail.vue')
  },
  {
    path: '/repository',
    name: 'repository',
    component: () => import('../views/repository.vue')
  }
]

const router = new VueRouter({
  routes: routers
})

export default router
