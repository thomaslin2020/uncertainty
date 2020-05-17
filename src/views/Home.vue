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
                        <b-checkbox style="display: inline-block; margin-right: 10px" v-model="round_data"><p
                                style="font-size: 18px">
                            <strong>Round</strong></p></b-checkbox>
                        <b-input style="display: inline; width: 105px; margin-right: 10px" v-if="round_data"
                                 placeholder="# of sigfigs" v-model="sigfigs"></b-input>
                        <label for="mode" style="vertical-align: middle;"><strong>Mode:</strong></label><select
                            id="mode" class="input-button"
                            v-model="mode">
                        <option value="simple" selected="selected">Simple</option>
                        <option value="standard">Standard</option>
                    </select>
                        <b-checkbox v-if="!isMobile" style="display: inline-block; margin-right: 10px"
                                    v-model="showGraph"><p
                                style="font-size: 18px">
                            <strong>Show Progress</strong></p></b-checkbox>
                        <div style="display: inline-block">
                            <b-button class="input-button" @click="send" type="submit" value="upload">Calculate
                            </b-button>
                            <b-button class="input-button" @click="showDescription = !showDescription">
                                <template v-if="!showDescription">Show Description</template>
                                <template v-else>Hide Description</template>
                            </b-button>
                        </div>
                    </div>
                </div>
                <br>
                <div class="description" v-show="showDescription">
                    <div style="background: white; border-radius: 10px;
        border: 4px solid rgba(0, 0, 0, 0.2); padding: 15px 15px 15px 30px;">
                        <div>
                            <h2>Description</h2>
                            <p><strong>U(a,b)</strong> represents the uncertainty value <strong>a ± b</strong> (e.g. (2
                                ± 1) = U(1,2))</p>
                            <p><strong>Operations that can be used include:</strong></p>
                            <ul>
                                <li>Basic Operations: Addition(+), Subtraction(-), Multiplication(⨉), Division(÷),
                                    Power(^)
                                </li>
                                <li>Trigonometric functions: sin, cos, tan, arcsin, arccos, arctan</li>
                                <li>Exponential and logarithmic functions: log (default base 10), ln, exp</li>
                                <li>Other operations: square (sq), square root (sqrt), cube root (cbrt)</li>
                            </ul>
                            <p><strong>Constants:</strong></p>
                            <ul>
                                <li>pi (π) , e, tau (τ)</li>
                            </ul>
                            <p><strong>Example: </strong></p>
                            <pre><code style="white-space: normal;">pi+sin(U(1.0,0.1))*U(2.0,0.1)^2/log(sqrt(U(3.0,0.1))) </code></pre>
                            <p><strong>Rounding:</strong></p>
                            <p>Uncertainty values are rounded to 1 sig fig. Values are rounded based on the smallest
                                decimal
                                of the uncertainty value. The maximum number of sig figs is limited to the maximum
                                number of
                                sig figs of the input value.</p>
                            <p><strong>Examples: </strong></p>
                            <ul>
                                <li>U(1.0,0.01) round to 3 sig figs = U(1,0)</li>
                                <li>U(555,55) round to 3 sig figs = U(555,60)</li>
                                <li>U(555,55) round to 2 sig figs = U(560,60)</li>
                            </ul>
                        </div>
                    </div>
                    <br>
                </div>
                <h2>Result: {{result}}</h2>
                <div v-if="dotData" style="display: flex;
        flex-direction: column;
        justify-content: center;">
                    <graph-viz :dot-data="dotData"></graph-viz>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    import axios from 'axios'
    import graphViz from "../components/graphViz";

    export default {
        name: 'Home',
        components: {
            graphViz,
        },
        data() {
            return {
                result: 'None',
                equation: "",
                mode: 'simple',
                showGraph: false,
                dotData: "",
                round_data: false,
                sigfigs: "",
                showDescription: true,
                isMobile: this.mobileCheck()
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
            mobileCheck: function () {
                let check = false;
                (function (a) {
                    if (/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino/i.test(a) || /1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw(n|u)|c55\/|capi|ccwa|cdm|cell|chtm|cldc|cmd|co(mp|nd)|craw|da(it|ll|ng)|dbte|dcs|devi|dica|dmob|do(c|p)o|ds(12|d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(|_)|g1 u|g560|gene|gf5|gmo|go(\.w|od)|gr(ad|un)|haie|hcit|hd(m|p|t)|hei|hi(pt|ta)|hp( i|ip)|hsc|ht(c(| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i(20|go|ma)|i230|iac( ||\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|[a-w])|libw|lynx|m1w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|mcr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30([02])|n50([025])|n7(0([01])|10)|ne(([cm])-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan([adt])|pdxg|pg(13|([1-8]|c))|phil|pire|pl(ay|uc)|pn2|po(ck|rt|se)|prox|psio|ptg|qaa|qc(07|12|21|32|60|[2-7]|i)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h|oo|p)|sdk\/|se(c(|0|1)|47|mc|nd|ri)|sgh|shar|sie(|m)|sk0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h|v|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl|tdg|tel(i|m)|tim|tmo|to(pl|sh)|ts(70|m|m3|m5)|tx-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c([- ])|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas-|your|zeto|zte-/i.test(a.substr(0, 4))) check = true;
                })(navigator.userAgent || navigator.vendor || window.opera);
                console.log(check)
                return check;
            },
            send() {
                this.showDescription = false
                if (this.equation.length !== 0) {
                    const fd = new FormData()
                    this.equation += ')'.repeat(this.count(this.equation, '(') - this.count(this.equation, ')'))
                    let equation = this.equation.replace("^", "**")
                    this.sigfigs = this.sigfigs.replace(/\s/g, '')
                    if (this.sigfigs !== 'max') {
                        this.sigfigs = this.sigfigs.replace(/\D/g, '')
                    }
                    if (this.sigfigs.length === 0 && this.round_data === true) {
                        this.sigfigs = "max"
                    }
                    if (this.round_data) {
                        if (this.sigfigs === 'max') {
                            equation = "r(" + this.equation + ",32)"
                            fd.append('round', '32')
                        } else {
                            equation = "r(" + this.equation + "," + this.sigfigs + ")"
                            fd.append('round', this.sigfigs)
                        }
                    } else {
                        fd.append('round', '-1')
                    }
                    fd.append('method', this.mode)
                    fd.append('showGraph', this.showGraph.toString())
                    fd.append('equation', equation)
                    this.result = "loading..."
                    axios.post('https://thomaslin2020.pythonanywhere.com/api/calculate', fd)
                        .then(response => {
                            this.result = response.data.result
                            this.dotData = response.data.graph
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

    p {
        text-align: left;
    }

    li {
        margin-left: 1em;
        text-align: left;
    }
</style>