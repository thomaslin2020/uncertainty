<template>
    <div id="home">
        <div style="display: flex;  justify-content: center; align-items: center;">
            <div style="width: 80%">
                <h1>Equation</h1>
                <br>
                <b-input type="text" id="equation" name="equation"></b-input>
                <br>
                Choose your mode:
                <input type="radio" id="simple" value="simple" v-model="mode">
                <label for="simple">Simple</label>
                &nbsp;
                <input type="radio" id="standard" value="standard" v-model="mode">
                <label for="standard">Standard</label>
                <br>
                <br>
                <b-button type="submit" value="upload" @click="send">Calculate</b-button>
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
                axios.post('https://thomaslin2020.pythonanywhere.com/', fd)
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