module.exports = {
    outputDir: 'dist',
    baseUrl: IS_PRODUCTION ? 'https://uncertainty-calculator.herokuapp.com/' : '/',
    publicPath: process.env.NODE_ENV === 'production'
        ? '/uncertainty/'
        : '/'
}