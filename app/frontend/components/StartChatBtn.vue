<template>
  <b-button class="mr-1" variant="info" @click="startChat">
    Send message
  </b-button>
</template>

<script>
import get_cookie from "@/cookie";

export default {
  name: 'StartChatBtn',
  props: {
    profileId: Number,
    chatUrl: String,
  },
  data: function () {
    return {
      loading: false,
      type: 'direct'
    }
  },
  methods: {
    startChat: async function () {
      this.loading = true;

      const response = await fetch(this.chatUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'JWT ' + get_cookie('auth_token'),
        },
        body: JSON.stringify({
          type: this.type,
          profile_id: this.profileId
        })
      });
      const data = await response.json();

      if (data.success) {
        window.location.href = '/dialogs/';
      }

      this.loading = false;
    }
  }
}
</script>
