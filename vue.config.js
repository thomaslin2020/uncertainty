module.exports = {
    outputDir: 'dist',
<<<<<<< HEAD
    publicPath: process.env.NODE_ENV === 'production' ? 'https://uncertainty-calculator.herokuapp.com/' : '/'
=======
    baseUrl: IS_PRODUCTION ? 'https://uncertainty-calculator.herokuapp.com/' : '/',
    publicPath: process.env.NODE_ENV === 'production'
        ? '/uncertainty/'
        : '/'
>>>>>>> parent of 498217e... Update vue.config.js
}