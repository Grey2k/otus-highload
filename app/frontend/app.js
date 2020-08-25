import Vue from 'vue'
import { BootstrapVue, IconsPlugin } from 'bootstrap-vue'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import Friendship from './components/Friendship.vue'
import PostForm from "@/components/PostForm";
import Feed from "@/components/Feed";

Vue.use(BootstrapVue)
Vue.use(IconsPlugin)

Vue.component('v-friendship', Friendship)
Vue.component('v-post-form', PostForm)
Vue.component('v-feed', Feed)

new Vue({
  el: '#vapp'
})