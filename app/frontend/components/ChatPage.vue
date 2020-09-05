<template>
  <b-row>
    <b-col lg="2">
        <v-chat-list :chat-list-url="chatListUrl" @open-chat="onOpenChat"></v-chat-list>
    </b-col>
    <b-col lg="10" class="border-left">
        <v-chat v-if="activeChat" :chat-url="chatUrl" :profile-id="profileId" :chat-id="activeChat"></v-chat>
    </b-col>
</b-row>
</template>

<script>
export default {
  name: 'ChatPage',
  props: {
    chatListUrl: String,
    chatUrl: String,
    profileId: Number,
  },
  data: function () {
    return {
      activeChat: null
    };
  },
  methods: {
    onOpenChat: function (id) {
      this.activeChat = id;
    }
  }
}
</script>
