<template>
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
</template>

<script>
    import VueTableDynamic from 'vue-table-dynamic'

    export default {
        name: "Table",
        components: {VueTableDynamic},
        props: ['data'],
        data() {
            return {
                params: {
                    data: this.data,
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
            onCellChange(rowIndex, columnIndex, data) {
                data = data.replace(/\D/g, '')
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