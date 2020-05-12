<template>
    <div>
        <h1>This is a Guide Page</h1>
        <highlightable-input
                highlight-style="background-color:yellow"
                :highlight-enabled="highlightEnabled"
                :highlight="highlight"
                v-model="msg"
        />
    </div>
</template>
<script>

    import HighlightableInput from "vue-highlightable-input"

    export default {
        name: 'Guide',
        components: {
            HighlightableInput
        },
        data() {
            return {
                msg: '',
                highlight: [
                    {text: 'chicken', style: "background-color:#f37373"},
                    {text: 'noodle', style: "background-color:#fca88f"},
                    {text: 'soup', style: "background-color:#bbe4cb"},
                    {text: 'so', style: "background-color:#fff05e"},
                    "whatever",
                    {start: 2, end: 5, style: "background-color:#f330ff"}
                ],
                highlightEnabled: true
            }
        },
    }
</script>

<style scoped>
    .input-parent {
        display: flex;
        flex-direction: row;
        justify-content: center;
    }

    .input-button {
        margin-right: 10px;
        margin-left: 10px;
    }
</style>