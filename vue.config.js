module.exports = {
    outputDir: 'dist',
    baseUrl: process.env.NODE_ENV === 'production' ? 'https://uncertainty-calculator.herokuapp.com/' : '/'
,    publicPath: process.env.NODE_ENV === 'production'
        ? '/uncertainty/'
        : '/'
}