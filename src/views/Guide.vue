<template>
    <div>
        <div style="display: inline-block">
            <h3>Try it</h3>

        </div>
    </div>
</template>

<script>

    export default {
        name: 'HelloWorld',
        components: {},
        data() {
            return {
                msg: 'A bold new future hacker news',
                defaultStyle: {'background-color': 'purple', 'color': 'white'},
                highlight: [
                    {text: 'hacker news', style: "background-color:#ff6600"},
                    {text: 'CASEsensitive', style: "background-color:#fca88f", caseSensitive: true},
                    {text: '@Soup', style: "background-color:#bbe4cb"},
                    {text: 'comic-sans', style: "font-family:comic-sans"},
                    {text: 'bold', style: "font-weight: bold;"},
                    "whatever",
                    {start: 0, end: 1, style: "border: 3px solid #AAAD21;"},
                    {start: 3, end: 5, style: "border: 2px solid #73AD21;"},
                    {
                        text: /[+]?[(]?[0-9]{3}[)]?[-\s.]?[0-9]{3}[-\s.]?[0-9]{4,6}/img,
                        style: "color: white; background-color:#aa2313"
                    }, // Phone number regex
                    {text: /{{\w+}}/gm, style: 'color: green;'},
                    {text: /{{.*?}}/gm, style: 'color: red'},
                    {text: /{{\w+/gm, style: 'color: green'},
                ],
                highlightEnabled: true,
                caseEnabled: false,
                customHighlight: ''
            }
        },
    }
</script>

<style scoped>
</style>