<template>
    <div>
        <h1>This is a Guide Page</h1>
        <div class="parent">
            <div style="width: 90%; max-width: 100%;">
                <vue-table-dynamic
                        :params="params"
                        @cell-change="onCellChange"
                        ref="table"
                >
                </vue-table-dynamic>
            </div>
        </div>
    </div>
</template>
<script>
    import VueTableDynamic from 'vue-table-dynamic'

    export default {
        name: "Guide",
        components: {VueTableDynamic},
        data() {
            return {
                params: {
                    data: [
                        ['Index', 'Data1', 'Data2', 'Data3'],
                        [1, '23', '7c95f7', '9a3853'],
                        [2, 'ec0b78', 'ba045d', 'ecf03c'],
                        [3, '63788d', 'a8c325', 'aab418']
                    ],
                    header: 'row',
                    stripe: true,
                    edit: {},
                    border: true,
                    columnWidth: [{column: 0, width: 50}],
                    showCheck: true
                }
            }
        },
        methods: {
            onCellChange(rowIndex, columnIndex, data) {
                console.log('onCellChange: ', rowIndex, columnIndex, data)
                console.log('table data: ', this.$refs.table.getData())
            },
        },
        mounted() {
            this.params.edit.column = Array.from({length: this.params.data[0].length - 1}, (_, i) => i + 1)
        }
    }
</script>

<style scoped>
    .parent {
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
</style>