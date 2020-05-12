<template>
    <div>
        <h1>This is a Tools Page</h1>
        <p>A collection of tools</p>
        <div class="parent-container">
            <div class="border-container">
                <div class="info-container">
                    <h3>UnitConverters.net: <a href="https://www.unitconverters.net/">Visit the Website</a></h3>
                    <vs-button @click="unitConverterActive=true" color="primary" type="filled">Preview</vs-button>
                    <vs-popup fullscreen title="Unit Converter" :active.sync="unitConverterActive">
                        <iframe width="100%" height="600px" src="https://www.unitconverters.net/"></iframe>
                    </vs-popup>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    export default {
        data() {
            return {
                unitConverterActive: false
            }
        }
    }
</script>
<style scoped>
    .parent-container{
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .info-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
        width: 80%;
        max-width: 80%;
        margin-top: 20px;
        margin-bottom: 20px;
    }
    .border-container{
        display: flex;
        flex-direction: row;
        justify-content: center;
        width: 80%;
        max-width: 80%;
        background: rgba(255,255,255,0.6);
        border-width: 2px;
        border-color: blue;
        border-radius: 10px;
    }
</style>