import Vue from 'vue'
import App from './App.vue'
import BootstrapVue from "bootstrap-vue"
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import router from './router'
import {library} from '@fortawesome/fontawesome-svg-core'
import {faGithub, faInstagram, faWeixin} from '@fortawesome/free-brands-svg-icons'
import {FontAwesomeIcon} from '@fortawesome/vue-fontawesome'
import {faEnvelope} from '@fortawesome/free-solid-svg-icons'
import VueTableDynamic from 'vue-table-dynamic'

library.add(faGithub, faInstagram, faWeixin, faEnvelope)
Vue.component('font-awesome-icon', FontAwesomeIcon)
Vue.use(BootstrapVue);
Vue.use(VueTableDynamic)

Vue.config.productionTip = false

new Vue({
    router,
    render: h => h(App)
}).$mount('#app')
