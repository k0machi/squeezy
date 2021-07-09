const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

module.exports = {
    plugins: [new MiniCssExtractPlugin()],
    mode: 'development',
    entry: {
        main: './assets/app.js',
        aclEditor: './assets/AclEditor/acl-editor.js',
        directiveEditor: './assets/DirectiveEditor/directive-editor.js'
    },
    output: {
        path: path.resolve(__dirname, 'static/dist'),
        filename: '[name].bundle.js',
    },
    resolve: {
        alias: {
            svelte: path.resolve('node_modules', 'svelte')
        },
        extensions: ['.mjs', '.js', '.svelte'],
        mainFields: ['svelte', 'browser', 'module', 'main']
    },
    module: {
        rules: [{
            test: /\.css$/,
            use: [MiniCssExtractPlugin.loader, 'css-loader']
        },
        {
            test: /\.svelte$/,
            use: 'svelte-loader'
        },
        {
            test: /node_modules\/svelte\/.*\.mjs$/,
            resolve: {
                fullySpecified: false
            }
        }],
    },
};