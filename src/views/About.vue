<template>
    <div class="about">
        <h1>About this Calculator</h1>
        <div class="parent-container">
            <div style="width: 88%">
                <p>This is a website for performing calculations involving unknown quantities using error propagation.
                    Calculations may involve algebraic expressions such as: <strong>addition</strong>,
                    <strong>subtraction</strong>, <strong>multiplication</strong>, <strong>division</strong>, <strong>trigonometric
                        functions</strong>, <strong>logarithms</strong>, … etc.</p>

                <h2>What is uncertainty?</h2>

                <p>Uncertainty is a parameter associated with results of measurements that defines the reasonable range
                    of
                    values attributed to the measured quantity. When reporting values with uncertainty, the uncertainty
                    indicates the <strong>estimated</strong> degree of error of the measurement. </p>

                <h2>Why is calculating uncertainty important?</h2>

                <p>In most experiments that you will encounter, most measured data isn’t perfect. Uncertainty gives a
                    quantitative indication of the result, which represents how well the result represents the value of
                    the measured quantity, allowing people to asses the reliability of the measurements.</p>

                <h2>Error vs Uncertainty</h2>

                <ul>
                    <li><strong>Error</strong> is the difference between a measurement and the true value of the
                        quantity of measurement
                    </li>
                    <li><strong>Uncertainty</strong> is the range of values which the true value is asserted to lie</li>
                </ul>

                <h2>Types of uncertainties:</h2>

                <h3><strong>Random uncertainties</strong></h3>

                <ul>
                    <li>Every apparatus has its associated degree of random uncertainty</li>
                    <li>Not biased in one direction or the other of the measurement</li>
                    <li>These errors <strong>cannot be eliminated</strong></li>
                </ul>

                <div style="text-align: left">
                    <strong>Analog and Digital</strong>
                </div>
                <ul>
                    <li>The uncertainty of any <strong>analog</strong> measuring instrument is ± <strong>half</strong>
                        of
                        the smallest division
                    </li>
                    <li>The uncertainty of any <strong>digital</strong> measuring instrument is ± the
                        <strong>smallest</strong> division
                    </li>
                </ul>

                <div style="text-align: left">
                    <strong>Other random uncertainties:</strong>
                </div>
                <ul>
                    <li>Time measurement - response time of hitting a stopwatch</li>
                    <li>Detecting color changes in an experiment</li>
                    <li><strong>They must be mentioned when they apply, even though quantitative data is not collected
                        based
                        on these observations</strong></li>
                </ul>

                <div style="text-align: left">
                    <strong>Properties:</strong>
                </div>
                <ul>
                    <li>Random <strong>errors</strong> (not uncertainty!) can be reduced by repeating the measurements
                        to
                        get a “best estimate” (average) and range (error margin)
                    </li>
                    <li>The experiment is <strong>reproducible</strong> and <strong>repeatable</strong></li>
                </ul>

                <h3><strong>Systematic Error:</strong></h3>

                <ul>
                    <li>Usually a result of poor experimental design</li>
                    <li>The errors will always be in the “same direction” (always greater / smaller)</li>
                    <li>Results can be <strong>precise</strong> but not <strong>accurate</strong></li>
                    <li><strong>Cannot</strong> be eliminated with repeated measurement</li>
                </ul>

                <p><strong>Precision</strong> - How close together the measurements are</p>

                <p><strong>Accuracy</strong> - How close to the true value of the measurements are </p>

                <p>Sources of systematic error: (cite this from textbook)</p>

                <ul>
                    <li>Instrumental (eg. Improperly calibrated)</li>
                    <li>Observational (eg. Parallax error)</li>
                    <li>Environmental (eg. Humidity &amp; temperature fluctuations)</li>
                    <li>Theoretical (eg. Procedure or calculation based on simplified models that make assumptions)</li>
                </ul>

                <p><em>All relevant errors <strong>must</strong> be addressed in the evaluation!</em></p>

                <h2>Rules of significant figures:</h2>

                <p>Write something here…</p>

                <h2>Calculating error:</h2>

                <div v-katex:display="'\\%error=\\frac{\\mid value - exact \\mid}{exact} \\times 100 \\%'"></div>

                <p>Further information: <a
                        href="https://chem.libretexts.org/Bookshelves/General_Chemistry/Map%3A_Chemistry_-_The_Central_Science_(Brown_et_al.)/01._Introduction%3A_Matter_and_Measurement/1.5%3A_Uncertainty_in_Measurement">Chemistry
                    LibreTexts</a></p>

                <h2>Rules for calculating uncertainty values</h2>

                <div>
                    <table :key="component">
                        <tr>
                            <th>Type</th>
                            <th>Example</th>
                            <th>Simple</th>
                            <th>Standard</th>
                        </tr>
                        <tr>
                            <td>
                                <i>Addition</i> or <i>Subtraction</i>
                            </td>
                            <td>
                                <div v-katex:display="'y=a+b-c'"></div>
                            </td>
                            <td>
                                <div v-katex:display="'\\Delta R=\\Delta a+ \\Delta b+ \\Delta c'"></div>
                            </td>
                            <td>
                                <div v-katex:display="'\\sigma_y=\\sqrt{\\sigma_a^2 +\\sigma_b^2+\\sigma_c^2}'"></div>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <i>Multiplication</i> or <i>Division</i>
                            </td>
                            <td>
                                <div v-katex:display="'y=\\frac{ab}{c}'"></div>
                            </td>
                            <td>
                                <div v-katex:display="'\\frac{\\Delta y}{y} =\\frac{\\Delta a}{a} + \\frac{\\Delta b}{b} + \\frac{\\Delta c}{c}'"></div>
                            </td>
                            <td>
                                <div v-katex:display="'\\frac{\\sigma_y}{y} =\\sqrt{\\Big(\\frac{\\sigma_a}{a}\\Big)^2 + \\Big(\\frac{\\sigma_b}{b}\\Big)^2 + \\Big(\\frac{\\sigma_c}{c}\\Big)^2}'"></div>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <i>Exponential</i>
                            </td>
                            <td>
                                <div v-katex:display="'y=a^x'"></div>
                            </td>
                            <td>
                                <div v-katex:display="'\\Delta y=\\left|n\\frac{\\Delta a}{a}\\right|'"></div>
                            </td>
                            <td>
                                <div v-katex:display="'\\sigma_y=\\left|n\\frac{\\sigma_a}{a}\\right|'"></div>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <i>General</i>
                            </td>
                            <td>
                                <div v-katex:display="'y=f(x)'"></div>
                            </td>
                            <td>
                                <div v-katex:display="'\\Delta y= f(x+\\Delta x) - f(x)'"></div>
                            </td>
                            <td>
                                <div v-katex:display="'\\sigma_y=\\left|\\frac{d f(x)}{dx}\\sigma_x\\right|'"></div>
                            </td>
                        </tr>
                    </table>
                </div>
                <br>

                <div class="figure-container">
                    <figure><img
                            src="https://www.cherrybiotech.com/wp-content/uploads/2018/06/Figure-1-e1530193488428.png"
                            alt="Image"/>
                        <figcaption>Image source: <a
                                href="https://www.cherrybiotech.com/scientific-note/accuracy-and-precision-in-measurements">Cherry
                            Biotech</a>
                        </figcaption>
                    </figure>
                </div>


            </div>
        </div>

    </div>
</template>

<script>
    export default {
        name: 'About',
        props: {},
        data() {
            return {
                random: 0,
                component: 0
            }
        },
        methods: {
            wait: function (ms) {
                let d = new Date();
                let d2 = null;
                do {
                    d2 = new Date();
                }
                while (d2 - d < ms);
                this.component += 1
            }
        },
        watch: {
            random: function () {
                console.log('data changed');
                this.$nextTick().then(() => {
                    this.random = Math.random()
                });
            }
        }
        ,
        mounted() {
            this.wait(100);
            this.$forceUpdate()
            this.component += 1
        }
    }
</script>

<style scoped>
    .parent-container {
        display: flex;
        flex-direction: row;
        justify-content: center;
        margin-top: 20px;
        margin-bottom: 10px;
    }

    p {
        text-align: left;
    }

    li {
        text-align: left;
    }

    h2 {
        text-align: left;
    }

    h3 {
        text-align: left;
        font-size: 20px;
    }

    figure {
        padding: 5px;
        margin: auto;
    }


    figcaption {
        font: italic smaller sans-serif;
        padding: 3px;
        text-align: center;
    }

    .figure-container {
        padding: 10px;
        background: #FFF;
        border-radius: 15px;
        border: 4px solid rgba(0, 0, 0, 0.2);
    }

    table {
        font-family: arial, sans-serif;
        border-collapse: collapse;
        width: 100%;
    }

    td, th {
        border: 1px solid #dddddd;
        text-align: left;
        padding: 8px;
    }

    tr:nth-child(odd) {
        background-color: #FFFFFF;
    }

    tr:nth-child(even) {
        background-color: #dddddd;
    }
</style>