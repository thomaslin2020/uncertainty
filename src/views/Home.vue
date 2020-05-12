<template>
    <div id="home">
        <div style="display: flex;  justify-content: center; align-items: center;">
            <div style="width: 80%">
                <h1>Uncertainty Calculator</h1>
                <br>
                <b-input id="equation" name="equation" type="text"
                         placeholder="Enter your equation"
                         v-model="equation"></b-input>
                <br>
                <div>
                    <label for="mode"><strong>Mode:</strong></label><select id="mode" class="input-button"
                                                                            v-model="mode">
                    <option value="simple" selected="selected">Simple</option>
                    <option value="standard">Standard</option>
                </select>
                    <label for="verbose"><strong>Level:</strong></label><select id="verbose" class="input-button"
                                                                                v-model="level">
                    <option value="-1">Simplest</option>
                    <option value="0" selected="selected">Normal (Combined)</option>
                    <option value="1">Normal</option>
                    <option value="2">Detailed (Combined)</option>
                    <option value="3" v-if="equation.length < 10">Detailed</option>
                </select>
                    <b-button class="input-button" @click="send" type="submit" value="upload">Calculate</b-button>
                </div>
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
                equation: "",
                mode: 'simple',
                level: "0"
            }
        },
        methods: {
            send() {
                if (this.equation.length !== 0) {
                    const fd = new FormData()
                    fd.append('method', this.mode)
                    fd.append('equation', document.getElementById('equation').value.replace("^","**"))
                    this.result = "loading..."
                    axios.post('https://uncertainty-calculator.herokuapp.com/api/calculate', fd)
                        .then(response => {
                            this.result = response.data
                            console.log(response)
                        }).catch(e => {
                        this.result = 'None'
                        console.log(e)
                    })
                } else {
                    this.result = "Please enter an equation"
                }
            }
        }
    }
</script>

<style scoped>

    .input-button {
        margin-right: 10px;
        margin-left: 10px;
    }
</style>