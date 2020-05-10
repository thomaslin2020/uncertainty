<template>
    <div id="home">
        <div style="display: flex;  justify-content: center; align-items: center;">
            <div style="width: 80%">
                <h1>Equation</h1>
                <br>
                <b-input id="equation" name="equation" type="text"></b-input>
                <br>
                Choose your mode:
                <input id="simple" type="radio" v-model="mode" value="simple">
                <label for="simple">Simple</label>
                &nbsp;
                <input id="standard" type="radio" v-model="mode" value="standard">
                <label for="standard">Standard</label>
                <br>
                <br>
                <b-button @click="send" type="submit" value="upload">Calculate</b-button>
                <br>
                <br>
                <h2>Result: {{result}}</h2>
            </div>
        </div>
    </div>
</template>

<script>
    import axios from 'axios'

    export default {
        name: 'Home',
        components: {},
        data() {
            return {
                result: 'None',
                mode: 'simple'
            }
        },
        methods: {
            send() {
                const fd = new FormData()
                fd.append('method', this.mode)
                fd.append('equation', document.getElementById('equation').value)
                axios.post('http://127.0.0.1:5001/', fd)
                    .then(response => {
                        this.result = response.data
                        console.log(response)
                    }).catch(e => {
                    console.log(e)
                })
            }
        }
    }
</script>