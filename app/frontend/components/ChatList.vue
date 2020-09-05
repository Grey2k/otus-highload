<template>

  <b-list-group flush>
    <b-spinner v-if="loading" variant="primary" class="m-5"></b-spinner>
    <b-list-group-item v-for="chat in chats" :key="chat.id">
      <b-link v-on:click="openChat(chat.id)">{{ chat.name }}</b-link>
    </b-list-group-item>
  </b-list-group>

</template>

<script>
import get_cookie from "@/cookie";

export default {
  name: 'ChatList',
  props: {
    chatListUrl: String,
  },
  mounted() {
    this.loadChats();
  },
  data: function () {
    return {
      chats: [],
      loading: true,
    }
  },
  methods: {
    openChat: function (id) {
      this.$emit('open-chat', id);
    },
    loadChats: async function () {
      //todo: сделать клиента для api-чатов
      const response = await fetch(this.chatListUrl, {
        headers: {
          'Authorization': 'JWT ' + get_cookie('auth_token'),
        }
      });
      const data = await response.json();

      this.chats = data.items;
      this.loading = false;
    }
  }
}
</script>
