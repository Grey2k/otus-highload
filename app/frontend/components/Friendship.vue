<template>
    <div>
        <b-button class="mr-1" variant="success" v-if="!isFriends && !inviteReceived && !inviteSent" v-on:click="addFriend">
            Add to friends
        </b-button>

        <b-button class="mr-1" variant="success" v-if="inviteReceived && !isFriends" v-on:click="addFriend">
            Accept friendship
        </b-button>

        <b-button class="mr-1" variant="danger" v-if="inviteReceived  && !isFriends" v-on:click="removeFriend">
            Reject friendship
        </b-button>

        <b-button class="mr-1" variant="danger" v-if="isFriends" v-on:click="removeFriend">
            Remove from friends
        </b-button>

        <b-alert show v-if="inviteSent && !isFriends">Friendship invite sent</b-alert>
    </div>
</template>

<script>
    export default {
        name: 'Friendship',
        props: {
            friend: String,
            is_friends: String,
            invite_received: String,
            invite_sent: String,
        },
        data: function () {
            return {
                isFriends: this.is_friends === 'True',
                inviteReceived: this.invite_received === 'True',
                inviteSent: this.invite_sent === 'True',
                friendId: this.friend,
            }
        },
        methods: {
            addFriend: function () {
                const formData = new FormData();
                formData.append('friend_id', this.friendId)
                this.inviteSent = true;
                if (this.inviteReceived) {
                    this.isFriends = true;
                }
                fetch('/friends/add', {
                    'method': 'POST',
                    'body': formData
                })
            },
            removeFriend: function () {
                const formData = new FormData();
                formData.append('friend_id', this.friendId)

                this.inviteSent = false;
                this.inviteReceived = false;
                this.isFriends = false;
                fetch('/friends/delete', {
                    'method': 'POST',
                    'body': formData
                })
            }
        }
    }
</script>
