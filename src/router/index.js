import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '../views/Home.vue'

Vue.use(VueRouter)

const routes = [
    {
        path: '/',
        name: 'Home',
        component: Home
    },
    {
        path: '/guide',
        name: 'Guide',
        component: () => import('../views/Guide.vue')
    },
    {
        path: '/table',
        name: 'TableCalculation',
        component: () => import('../views/TableCalculation.vue')
    },
    {
        path: '/about',
        name: 'About',
        component: () => import('../views/About.vue')
    },
    {
        path: '/tools',
        name: 'Tools',
        component: () => import('../views/Tools.vue')
    },
    {path: '*', redirect: {name: 'Home'}}
]

const router = new VueRouter({
    routes
})

export default router