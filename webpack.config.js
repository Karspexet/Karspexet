/* global  __dirname module */
var path = require("path"),
    BundleTracker = require("webpack-bundle-tracker"),
    ExtractTextPlugin = require("extract-text-webpack-plugin")

module.exports = {
    context: __dirname,

    entry: {
        app: "./assets/js/app.js",
        style: "./assets/css/main.css"
    },

    output: {
        path: path.resolve("./assets/bundles/"),
        filename: "[name]-[hash].js"
    },

    plugins: [
        new BundleTracker({filename: "./webpack-stats.json"}),
        new ExtractTextPlugin("[name]-[hash].css"),
    ],

    module: {
        loaders: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                loader: "babel-loader",
                query: {
                    presets: ["es2015"]
                }
            },
            {
                test: /\.css$/,
                exclude: /node_modules/,
                loader: ["style-loader", "css-loader"]
            }
        ],
        rules: [
            {
                test: /\.css$/,
                use: ExtractTextPlugin.extract({
                    fallback: "style-loader",
                    use: ["css-loader"]
                })
            }
        ]
    },

    devtool: "source-map"
}
