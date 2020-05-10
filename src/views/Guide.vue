<template>
    <div>
        <h1>This is a Guide Page</h1>
        <div style="width: 600px">
            <vue-table-dynamic
                    :params="params"
                    @cell-change="onCellChange"
                    ref="table"
            >
            </vue-table-dynamic>
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
                        [1, 'b3ba90', '7c95f7', '9a3853'],
                        [2, 'ec0b78', 'ba045d', 'ecf03c'],
                        [3, '63788d', 'a8c325', 'aab418']
                    ],
                    header: 'row',
                    stripe: true,
                    edit: {
                        row: [1],
                        column: [1],
                        cell: [[-1, -1]]
                    }
                }
            }
        },
        methods: {
            onCellChange(rowIndex, columnIndex, data) {
                console.log('onCellChange: ', rowIndex, columnIndex, data)
                console.log('table data: ', this.$refs.table.getData())
            }
        },
    }
</script>

<style scoped>

</style>