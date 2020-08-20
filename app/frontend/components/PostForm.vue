<template>
  <div>
    <b-button class="create-post" variant="primary" v-b-modal.create-post-modal>
      <b-icon icon="plus-circle" font-scale="2"></b-icon>
    </b-button>
    <b-modal
        id="create-post-modal"
        title="New post"
        ok-only
        ok-title="Publish"
        @ok="createPost"
    >
      <b-form-textarea
          :state="isValid"
          rows="10"
          class="mb-3"
          placeholder="Tell something"
          v-model="content"
      ></b-form-textarea>
    </b-modal>
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
    createPost: async function (bvModalEvt) {
      bvModalEvt.preventDefault()

      const formData = new FormData()
      formData.append('content', this.content)


      const response = await fetch(this.submitUrl, {
        'method': 'POST',
        'body': formData,
      })

      const data = await response.json()
      this.isValid = data.success ? null : false
      if (!data.success) {
        return
      }
      if (data.redirect) {
        location.href = data.redirect
      }
      this.$nextTick(() => {
        this.$bvModal.hide('create-post-modal')
      })
    }
  }
}
</script>
<style>
.create-post {
  border-radius: 50%;
  width: 50px;
  height: 50px;
  position: fixed;
  bottom: 30px;
  right: 30px;
  z-index: 99;
  padding: 0;
}
</style>