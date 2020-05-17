<template>
    <div>
        <h1>About Us</h1>
        <div class="parent-container">
            <div style="width: 88%">
                <p>We are a team of high-school programmers in Canada. Having experienced much frustration when
                    calculating the uncertainty values for our lab reports, we have discovered that current online
                    uncertainty calculators do not fulfill our needs. Inspired by uncertainty calculators of <a
                            href="http://web.mst.edu/~gbert/JAVA/uncertainty.HTML">Professor Bertrand from University of Missouri-Rolla</a>
                    and <a href="http://denethor.wlu.ca/data/xc.shtml">Wilfrid Laurier University</a>, we have
                    designed our uncertainty calculator, which supports multi-step calculations with both maximum and
                    standard errors, as well as accurate rounding of significant figures. In addition, computational
                    graphs were added to help visualize the calculation process. Those who are interested in programming
                    may also use this as a visualization tool for the order of operations in infix
                    postfix conversion operations. We hope that this calculator can help many people who are also in a
                    similar situation and that the interactive nature of this calculator could provide more insight to
                    new learners of this topic. Feel free to contact us and submit additional feature requests.</p>

                <p style="text-align: right;">– <a href="https://github.com/thomaslin2020">Thomas</a> and <a href="https://github.com/DexuanMeng">David</a></p>

                <p>Thanks to Julia for her support throughout the project.</p>

            </div>
        </div>

    </div>
</template>

<script>
    export default {
        name: "About"
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
</style>