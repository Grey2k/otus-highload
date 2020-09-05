import Vue from 'vue'
import {BootstrapVue, IconsPlugin} from 'bootstrap-vue'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import Friendship from './components/Friendship.vue'
import PostForm from "@/components/PostForm";
import Feed from "@/components/Feed";
import ChatList from "@/components/ChatList";
import Chat from "@/components/Chat";
import ChatPage from "@/components/ChatPage";
import StartChatBtn from "@/components/StartChatBtn";

Vue.use(BootstrapVue)
Vue.use(IconsPlugin)

Vue.component('v-friendship', Friendship)
Vue.component('v-post-form', PostForm)
Vue.component('v-feed', Feed)
Vue.component('v-chat-list', ChatList)
Vue.component('v-chat', Chat)
Vue.component('v-chat-page', ChatPage)
Vue.component('v-chat-btn', StartChatBtn)

new Vue({
    el: '#vapp',
})