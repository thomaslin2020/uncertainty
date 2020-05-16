<template>
    <div class="pa-2">
        <p>Hello</p>
        <graph-viz :dot-data="dotData"></graph-viz>
    </div>

</template>
<script>
    import graphViz from "../components/graphViz";

    export default {
        name: 'HelloWorld',
        data() {
            return {
                dotData: "digraph {\n\t0 [label=\"(1±2)\"]\n}",
            };
        },
        components: {
            graphViz,
        },
    }
</script>

<style scoped>
    .input {
        position: fixed;
        bottom: 0;
        left: 0;
        top: 56px;
        width: 100%;
        height: 100%;
    }

    .image {
        position: fixed;
        top: 80px;
        left: 50%;
    }
</style>
