const path = require('path')

module.exports = {
    filenameHashing: false,
    runtimeCompiler: true,
    outputDir: path.join(__dirname, 'static', 'build'),
    configureWebpack: {
        resolve: {
            alias: {
                '@': path.join(__dirname, 'frontend')
            }
        },
        entry: {
            app: path.join(__dirname, 'frontend', 'app.js')
        }
    },
    chainWebpack: config => {
        config.plugins.delete('html')
        config.plugins.delete('preload')
        config.plugins.delete('prefetch')
    }
}