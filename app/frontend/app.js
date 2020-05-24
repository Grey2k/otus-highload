import Vue from 'vue'
import { BootstrapVue, IconsPlugin } from 'bootstrap-vue'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import Friendship from './components/Friendship.vue'

Vue.use(BootstrapVue)
Vue.use(IconsPlugin)

Vue.component('v-friendship', Friendship)

new Vue({
  el: '#vapp'
})