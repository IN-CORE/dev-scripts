let path = require("path");

process.env.NODE_ENV = "test";

let reporters = [];

/*
if(process.argv.some(isDebug)) {
	reporters = ["mocha"];
}

function isDebug(argument) {
	return argument === "--debug";
}*/

module.exports = function (config) {
	config.set({
		browsers: ["ChromeHeadless", "Firefox"],
		singleRun: true,
		colors: true,
		basePath: "",
		frameworks: ["jasmine", "sinon"],
		preprocessors: {
			"test/**/*.test.js": ["webpack", "sourcemap"]
		},
		files: [
			"node_modules/babel-polyfill/dist/polyfill.js",
			// {pattern: "test/resources/*.*", included: false, served: true},
			{pattern: "./test/resources/seaside_bldg.dbf", included: false, served: true},
			{pattern: "test/**/*.test.js"}
		],
		reporters: ["progress"],
		/* coverageReporter: {
			reporters: [
				{
					type: "text-summary"
				},
				{
					type: "html",
					dir: "coverage"
				}
			]
		}, */
		webpack: {
			devtool: "inline-source-map",
			resolve: {
				extensions: [".js", ".jsx"]
			},
			module: {
				exprContextCritical: false,
				rules: [
					{
						enforce: "pre",
						test: /\.jsx?$/,
						exclude: [path.resolve("node_modules")],
						loaders: ["babel-loader"]
					},
					{
						enforce: "pre",
						test: /\.css$/,
						include: [path.resolve("node_modules"), path.resolve("src")],
						loaders: ["style-loader", "css-loader?sourceMap"]
					}
				]
			},
			externals: {
				"react/addons": true,
				"react/lib/ExecutionEnvironment": true,
				"react/lib/ReactContext": true
			}
		},
		webpackServer: {
			noInfo: true
		},
		plugins: [
			"karma-webpack",
			"karma-jasmine",
			"karma-sinon",
			// "karma-coverage",
			"karma-sourcemap-loader",
			"karma-chrome-launcher",
			"karma-firefox-launcher",
			"karma-phantomjs-launcher",
			// "karma-mocha-reporter"
		]
	});
};
