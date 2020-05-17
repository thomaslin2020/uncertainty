<template>
    <div>
        <h1>Calculations with Tables</h1>
        <div class="input-parent">
            <div style="width: 80%">
                <b-input name="columns-input" placeholder="Enter your variables" type="text"
                         v-model="input_value"></b-input>
                <br>
                <div>
                    <b-button @click="generate_table" class="input-button">Generate Table</b-button>
                    <b-button @click="clear_table" class="input-button">Clear Table</b-button>
                </div>
                <br>
            </div>
        </div>
        <div v-if="showTable">
            <div class="parent">
                <div style="width: 90%; max-width: 100%;">
                    <vue-table-dynamic
                            :key="refresh_key"
                            :params="params"
                            @cell-change="onCellChange" ref="table"
                    >
                    </vue-table-dynamic>
                </div>
            </div>
        </div>
        <div class="input-parent" v-if="showTable">
            <div style="width: 80%">
                <br>
                <b-input id="equation-input" name="equation-input" placeholder="Enter your equation"
                         type="text"></b-input>
                <br>
                <div>
                    <label for="mode"><strong>Mode:</strong></label><select class="input-button" id="mode"
                                                                            v-model="mode">
                    <option selected="selected" value="simple">Simple</option>
                    <option value="standard">Standard</option>
                </select>
                    <label for="verbose"><strong>Level:</strong></label><select class="input-button" id="verbose"
                                                                                v-model="level">
                    <option value="-1">Simplest</option>
                    <option selected="selected" value="0">Normal (Combined)</option>
                    <option value="1">Normal</option>
                    <option value="2">Detailed (Combined)</option>
                    <option value="3">Detailed</option>
                </select>
                    <b-button @click="calculate" class="input-button">Calculate</b-button>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
    import VueTableDynamic from 'vue-table-dynamic'
    import Vue from 'vue'

    export default {
        name: "TableCalculation",
        components: {VueTableDynamic},
        data() {
            return {
                input_value: "",
                columns: [],
                showTable: false,
                refresh_key: 0,
                mode: "simple",
                level: "0",
                params: {
                    data: [],
                    header: 'row',
                    stripe: true,
                    edit: {},
                    border: true,
                    columnWidth: [{column: 0, width: 50}],
                    showCheck: true,
                }
            }
        },
        methods: {
            generate_table: function () {
                this.input_value = this.input_value.trim().replace(/\W,/g, '')
                if (this.input_value.substring(this.input_value.length - 1) === ",") {
                    this.input_value = this.input_value.substring(0, this.input_value.length - 1)
                }
                if (this.input_value.substring(0, 1) === ",") {
                    this.input_value = this.input_value.substring(1, this.input_value.length)
                }
                this.showTable = this.input_value.length !== 0;
                let c = this.input_value.split(",")
                this.columns = c
                for (let i = 0; i < c.length; i++) {
                    c[i] = c[i].trim()
                }
                c.unshift("Index")
                let array = []
                let temp = []
                for (let i = 0; i < c.length; i++) {
                    temp.push(c[i])
                }
                array.push(temp)
                for (let i = 0; i < 5; i++) {
                    temp = []
                    temp.push(i)
                    for (let j = 1; j < c.length; j++) {
                        temp.push(0)
                    }
                    array.push(temp)
                }
                console.log(array)
                Vue.set(this.params, 'data', array)
                this.params.edit.column = Array.from({length: this.params.data[0].length - 1}, (_, i) => i + 1)
                this.refresh_key = Math.random()
            },
            clear_table: function () {
                for (let i = 1; i < this.params.data.length; i++) {
                    for (let j = 2; j < this.params.data[i].length; j++) {
                        this.params.data[i][j] = 0
                    }
                }
                this.refresh_key = Math.random()
            },
            calculate: function () {

            },
            onCellChange(rowIndex, columnIndex, data) {
                data = data.replace(/\D/g, '')
                console.log('onCellChange: ', rowIndex, columnIndex, data)
                console.log('table data: ', this.$refs.table.getData())
            },
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

    .parent {
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
</style>