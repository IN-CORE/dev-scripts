import React from "react";
import { Route, IndexRoute } from "react-router";

import App from "./components/App";
import HomePage from "./components/HomePage";

import config from "./app.config";

export default (
	<Route path={config.basePath} component={App}>
		<IndexRoute component={HomePage} />
		{/*<Route path="other" component={OtherPage} />*/}
		{/*<Route path="*" component={NotFoundPage} />*/}
	</Route>
);
