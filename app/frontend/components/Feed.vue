<template>
  <div>
    <b-list-group-item v-for="post in posts" :key="post.id">
      <h4>{{ post.author }} </h4>
      <div>{{ post.publish_date }}</div>
      <div>
        {{ post.content }}
      </div>
    </b-list-group-item>

    <b-list-group-item v-if="!posts">
      <p>Feed empty</p>
    </b-list-group-item>

  </div>
</template>

<script>
const io = require('socket.io-client');

export default {
  name: 'Feed',
  props: {
    list: Array,
    feedId: String,
    socketUrl: String,
  },
  mounted() {
    const socket = io(this.socketUrl, {transports: ['websocket'], query: {feed_id: this.feedId}});
    socket.on('connect', () => {
      console.log(socket.id);
    });
    socket.on('new-post', (post) => {
      this.addPost(post)
    })
  },
  data: function () {
    return {
      posts: [...this.list],
    }
  },
  methods: {
    addPost: function (post) {
      this.posts.unshift(post)
    }
  }
}
</script>