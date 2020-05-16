<template>
    <div></div>
</template>

<script>
    import Viz from "viz.js";

    const {Module, render} = require("viz.js/full.render.js");
    export default {
        name: "GraphVizRender",
        props: ["dotData"],
        watch: {
            dotData(dotData) {
                this.render(dotData);
            }
        },
        mounted() {
            if (this.dotData) {
                this.render(this.dotData);
            }
        },
        methods: {
            async render(data) {
                try {
                    const viz = new Viz({Module, render});
                    this.$el.innerHTML = await viz.renderString(data);
                    this.$emit("error", "");
                    this.$store.commit("createPanZoom");
                    if (document.querySelector("svg")) {
                        this.$store.commit(
                            "updateSVGSize",
                            document.querySelector("svg").getBBox()
                        );
                    }
                } catch (err) {
                    // render error to label later
                    console.log("error", err.message);
                    this.$emit("error", err.message);
                }
            }
        }
    };
</script>

<style scoped>

</style>