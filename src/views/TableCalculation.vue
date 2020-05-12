<template>
    <div>
        <h1>Calculations with Tables</h1>
        <div class="input-parent">
            <div style="width: 80%">
                <b-input id="columns-input" name="columns-input" type="text"
                         placeholder="Enter your variables"></b-input>
                <br>
                <div>
                    <b-button class="input-button" @click="parse_input">Generate Table</b-button>
                    <b-button class="input-button" @click="clear_table">Clear Table</b-button>
                </div>
                <br>
            </div>
        </div>
        <div v-if="showTable">
            <Table :data="this.generate_data(columns)" :key="input + refresh_key"></Table>
        </div>
        <div class="input-parent" v-if="showTable">
            <div style="width: 80%">
                <br>
                <b-input id="equation-input" name="equation-input" type="text"
                         placeholder="Enter your equation"></b-input>
                <br>
                <div>
                    <label for="mode"><strong>Mode:</strong></label><select id="mode" class="input-button" v-model="mode">
                    <option value="simple" selected="selected">Simple</option>
                    <option value="standard">Standard</option>
                </select>
                    <label for="verbose"><strong>Level:</strong></label><select id="verbose" class="input-button" v-model="level">
                    <option value="-1">Simplest</option>
                    <option value="0" selected="selected">Normal (Combined)</option>
                    <option value="1">Normal</option>
                    <option value="2">Detailed (Combined)</option>
                    <option value="3">Detailed</option>
                </select>
                    <b-button class="input-button">Calculate</b-button>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
    import Table from "../components/Table";

    export default {
        name: "TableCalculation",
        components: {Table},
        data() {
            return {
                columns: [],
                input: "",
                showTable: false,
                refresh_key: 0,
                mode: "simple",
                level: "0"
            }
        },
        methods: {
            parse_input: function () {
                let input = document.getElementById("columns-input").value.trim()
                this.showTable = input.length !== 0;
                let c = input.split(",")
                for (let i = 0; i < c.length; i++) {
                    c[i] = c[i].trim()
                }
                c.unshift("Index")
                this.columns = c
                this.input = input
            },
            generate_data: function (columns) {
                let array = []
                let temp = []
                for (let i = 0; i < columns.length; i++) {
                    temp.push(columns[i])
                }
                array.push(temp)
                for (let i = 0; i < 5; i++) {
                    temp = []
                    temp.push(i)
                    for (let j = 1; j < columns.length; j++) {
                        temp.push(0)
                    }
                    array.push(temp)
                }
                return array
            },
            clear_table: function () {
                this.refresh_key = Math.random()
            }
        },
        mounted() {
        }
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