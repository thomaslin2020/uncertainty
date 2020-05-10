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
        path: '/about',
        name: 'About',
        component: () => import('../views/About.vue')
    },
    {
        path: '/guide',
        name: 'Guide',
        component: () => import('../views/Guide.vue')
    },
    {
        path: '/tools',
        name: 'Tools',
        component: () => import('../views/Tools.vue')
    },
    {
        path: '/resources',
        name: 'Resources',
        component: () => import('../views/Resources.vue')
    },
    {path: '*', redirect: {name: 'Home'}}
]

const router = new VueRouter({
    routes
})

export default router