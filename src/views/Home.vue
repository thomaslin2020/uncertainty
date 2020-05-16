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
                <div class="options">
                    <div style="display: inline-block;vertical-align: middle">
                        <label for="mode" style="vertical-align: middle;"><strong>Mode:</strong></label><select
                            id="mode" class="input-button"
                            v-model="mode">
                        <option value="simple" selected="selected">Simple</option>
                        <option value="standard">Standard</option>
                    </select>
                        <b-checkbox style="display: inline-block; margin-right: 10px" v-model="showGraph"><p
                                style="font-size: 18px">
                            <strong>Show Progress</strong></p></b-checkbox>
                        <label for="verbose" style="vertical-align: middle;"><strong>Level:</strong></label><select
                            v-if="showGraph"
                            id="verbose" class="input-button"
                            v-model="level">
                        <option value="0">Normal</option>
                        <option value="1">Detailed</option>
                    </select>

                        <b-button class="input-button" @click="send" type="submit" value="upload">Calculate</b-button>
                    </div>
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
                level: "0",
                showGraph: false
            }
        },
        methods: {
            count: function (str, char) {
                let c = 0
                for (let i = 0; i < str.length; i++) {
                    if (str[i] === char) {
                        ++c;
                    }
                }
                return c
            },
            send() {
                if (this.equation.length !== 0) {
                    const fd = new FormData()
                    this.equation += ')'.repeat(this.count(this.equation, '(') - this.count(this.equation, ')'))
                    fd.append('method', this.mode)
                    fd.append('equation', this.equation.replace("^", "**"))
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

    .options {
        display: flex;
        flex-direction: row;
        justify-content: center;
        text-align: center;
    }

    label {
        font-size: 20px;
        margin: auto;
    }
</style>