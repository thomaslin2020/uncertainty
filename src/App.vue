<template>
    <div id="app">
        <div class="main-container">
            <div id="nav">
                <b-navbar id="nav_bar" toggleable="md" type="light" variant="light">
                    <b-navbar-brand style="padding-top: 0; padding-bottom: 0; margin-left: 0.375rem" to="/"><img
                            alt="Logo"
                            src="@/assets/icon.png" style="max-width: 50px;"/></b-navbar-brand>
                    <b-navbar-toggle id="collapse-button" target="nav-collapse"></b-navbar-toggle>
                    <b-collapse id="nav-collapse" is-nav>
                        <b-navbar-nav class="ml-auto">
                            <b-nav-item to="/">Home</b-nav-item>
                            <b-nav-item to="/about">About Us</b-nav-item>
                            <b-nav-item to="/guide">Quick Guide</b-nav-item>
                            <b-nav-item to="/tools">Tools</b-nav-item>
                        </b-navbar-nav>
                    </b-collapse>
                </b-navbar>
            </div>
            <br>
            <div class="parent">
                <div class="background-layer">
                    <br>
                    <router-view/>
                    <br>
                </div>
            </div>
            <br>
        </div>
        <footer class="footer page-footer font-small unique-color-dark ">
            <div class="footer-copyright text-center py-3">
                <div class="footer-text-container">
                    <div style="width: 88%; max-width: 100%; vertical-align: center;">
                        <div style="display: inline-flex; flex-direction: row;">
                            <a class="media-button" href="https://www.linkedin.com/in/chen-yuan-thomas-lin-6384a111b"
                               style="color: rgb(45,62,81) !important;">
                                <font-awesome-icon :icon="{ prefix: 'fab', iconName: 'linkedin' }"
                                                   class="fa fa-wechat"/>
                            </a>
                            <a class="media-button" href="https://www.instagram.com/tho_mas_marji/"
                               style="color: rgb(45, 62, 81) !important;">
                                <font-awesome-icon :icon="{ prefix: 'fab', iconName: 'instagram' }"
                                                   class="fa fa-instagram"/>
                            </a>
                            <a class="media-button" href="https://github.com/thomaslin2020/uncertainty"
                               style="color: rgb(45, 62, 81) !important;">
                                <font-awesome-icon :icon="{ prefix: 'fab', iconName: 'github' }" class="fa fa-github"/>
                            </a>
                            <a class="media-button" href="mailto:thomaslin910608@gmail.com"
                               style="color: rgb(45, 62, 81) !important;">
                                <font-awesome-icon class="fa fa-mail" icon="envelope"/>
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </footer>
    </div>
</template>

<style>
    .fa {
        font-size: 30px;
        text-align: center;
        text-decoration: none;
    }

    .fa:hover {
        opacity: 0.7;
    }

    #app {
        font-family: Avenir, Helvetica, Arial, sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        text-align: center;
        color: #2c3e50;
        background: linear-gradient(45deg, #00A8C5, #ecff7e);
    }

    #nav_bar {
        z-index: 10;
        position: sticky;
        top: 0;
        height: 100%;
        width: 100%;
    }

    #nav a {
        font-weight: bold;
        color: #2c3e50;
    }

    #nav a.router-link-exact-active {
        color: #42b983;
    }

    .main-container {
        min-height: 100vh;
    }

    .background-layer {
        background: rgba(255, 255, 255, 0.6);
        width: 80%;
        max-width: 80%;
        border-radius: 10px
    }

    .parent {
        display: flex;
        justify-content: center;
        align-items: center;
    }

    .footer {
        background-color: rgba(248, 249, 250, 0.8);
        height: 60px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .footer-text-container {
        display: flex;
        flex-direction: row;
        justify-content: center;
    }

    .media-button {
        margin-left: 10px;
        margin-right: 10px;
    }
</style>
