<template>
    <div>
        <b-button variant="success" v-if="!isFriends && !inviteReceived && !inviteSent" v-on:click="addFriends">Add to friends</b-button>
        <b-button variant="success" v-if="inviteReceived && !isFriends">Accept friendship</b-button>
        <b-button variant="danger" v-if="inviteReceived  && !isFriends">Reject friendship</b-button>
        <b-button variant="danger" v-if="isFriends">Remove from friends</b-button>
        <p v-if="inviteSent && !isFriends">Friendship invite sent</p>
    </div>
</template>

<script>
    export default {
        name: 'Friendship',
        props: {
            friend: String,
            is_friends: Boolean,
            invite_received: Boolean,
            invite_sent: Boolean,
        },
        data: function() {
            return {
                isFriends: this.is_friends,
                inviteReceived: this.invite_received,
                inviteSent: this.invite_sent,
                friendId: this.friend,
            }
        },
        methods: {
            addFriends: function () {
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
            }
        }
    }
</script>
