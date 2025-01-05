import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'
import AboutPage from '../views/AboutPage.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomePage
    },
    {
      path: '/about',
      name: 'about',
      component: AboutPage
    },
    {
      path: '/import',
      name: 'import',
      component: () => import('../views/ImportPage.vue')
    },
    {
      path: '/grouping',
      name: 'grouping',
      component: () => import('../views/GroupingPage.vue')
    },
    {
      path: '/display',
      name: 'display',
      component: () => import('../views/DisplayPage.vue')
    },
    {
      path: '/export',
      name: 'export',
      component: () => import('../views/ExportPage.vue')
    }
  ]
})

export default router
