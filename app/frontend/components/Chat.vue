<template>
  <div class="chat">
    <b-spinner v-if="loading" variant="primary" class="m-5"></b-spinner>
    <div v-if="chat">
      <h3 class="chat-title">{{ chat.name }}</h3>
      <div class="msg_history">
        <div :class="messageType(message)" v-for="message in messages" :key="message.id">
          <div class="msg">
            <p>{{ message.text }}</p>
            <span class="time_date">{{ message.created_at }}</span>
          </div>
        </div>
      </div>
      <div class="type_msg">
        <form @submit="addMessage">
          <div class="input_msg_write">
            <b-input type="text" autocomplete="off" required class="write_msg" name="text"
                     placeholder="Type a message" v-model="text"></b-input>
            <button class="msg_send_btn" type="submit">
              <b-icon icon="arrow-return-right" variant="primary"></b-icon>
            </button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<script>
import get_cookie from "@/cookie";

export default {
  name: 'Chat',
  props: {
    chatUrl: String,
    profileId: Number,
    chatId: Number || null,
  },
  data: function () {
    return {
      loading: false,
      chat: null,
      messages: [],
      text: '',
    }
  },
  mounted() {
    this.loadChat(this.chatId);
  },
  methods: {
    messageType: function (message) {
      return this.profileId === message.sender_id ? 'outgoing_msg' : 'incoming_msg';
    },
    loadChat: async function (chatId) {
      this.loading = true;
      //todo: сделать клиента для api-чатов
      const response = await fetch(this.chatUrl + '/v1/' + chatId, {
        headers: {
          'Authorization': 'JWT ' + get_cookie('auth_token'),
        }
      });
      const data = await response.json();

      this.chat = data.dialog;
      this.messages = data.messages;

      this.messages.filter(message => !message.is_read).forEach(this.readMessage)

      this.loading = false;
    },
    addMessage: async function (e) {
      e.preventDefault();
      if (!this.text) {
        return;
      }
      //todo: сделать клиента для api-чатов
      const request = fetch(this.chatUrl + '/v1/' + this.chatId, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'JWT ' + get_cookie('auth_token'),
        },
        body: JSON.stringify({message: this.text})
      });
      this.messages.push({
        id: 'pending_' + this.messages.length,
        text: this.text,
        created_at: new Date().toUTCString(),
        sender_id: this.profileId,
      });
      this.text = '';
      await request;
    },
    readMessage: function (message) {
      fetch(this.chatUrl + '/v1/' + this.chatId + '/' + message.id, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'JWT ' + get_cookie('auth_token'),
        }
      });
    }
  },
  watch: {
    chatId: function (chatId) {
      this.loadChat(chatId);
    }
  }
}
</script>
