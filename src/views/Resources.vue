<template>
    <div style="display: flex; flex-direction: row; justify-content: center;">
        <div style="width: 80%;max-width: 80%">
            <b-input v-model="searchTerm" placeholder="Start typing here..."></b-input>
            <div v-for="(name, key) in names" v-bind:key="key">
                <div v-html="matchName(name)"></div>
            </div>
            <!--            <b-input v-model="formula" cols="30" rows="10"></b-input>-->
            <!--            <br>-->
            <!--            <vue-mathjax :formula="formula"></vue-mathjax>-->
        </div>
    </div>
</template>

<script>

    export default {
        name: 'HelloWorld',
        data() {
            return {
                names: ['John', 'Johan', 'Deon', 'Derek', 'Alex', 'Alejandro'],
                searchTerm: ''
                // formula: '$$x = {-b \\pm \\sqrt{b^2-4ac} \\over 2a}.$$',
                // msg: 'Welcome to Your Vue.js App'
            }
        },
        methods: {
            matchName(current) {
                let reggie = new RegExp(this.searchTerm, "ig");
                let found = current.search(reggie) !== -1;
                return !found ? current : current.replace(reggie, '<b>' + this.searchTerm + '</b>');
            }
        }
    }
</script>
