const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

module.exports = {
    plugins: [new MiniCssExtractPlugin()],
    mode: 'development',
    entry: './assets/app.js',
    output: {
        path: path.resolve(__dirname, 'static/dist'),
        filename: 'app.js',
    },
    module: {
        rules: [{
            test: /\.css$/,
            use: [MiniCssExtractPlugin.loader, 'css-loader']
        }],
    },
};