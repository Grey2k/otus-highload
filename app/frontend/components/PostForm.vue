<template>
  <div class="mx-3 my-4 text-right">
    <b-form-textarea
        :state="isValid"
        rows="3"
        class="mb-3"
        placeholder="Tell something"
        v-model="content"
    ></b-form-textarea>
    <b-button variant="primary" v-if="true" v-on:click="createPost">
      Publish
    </b-button>
  </div>
</template>

<script>
export default {
  name: 'PostForm',
  props: {
    submitUrl: String,
  },
  data: function () {
    return {
      content: '',
      isValid: null,
    }
  },
  methods: {
    createPost: async function () {
      const formData = new FormData()
      formData.append('content', this.content)

      const response = await fetch(this.submitUrl, {
        'method': 'POST',
        'body': formData,
      })

      const data = await response.json()
      this.isValid = data.success ? null : false;
      if (data.redirect) {
        location.href = data.redirect
      }
    }
  }
}
</script>
