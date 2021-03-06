import React, { PropTypes } from "react";
import { Link, IndexLink } from "react-router";

global.__base = __dirname + "/";

const App = (props) => {
	return (
		<div>
			<IndexLink to="/">Home</IndexLink>
			{" | "}
			{/*<Link to="/other">Other</Link>*/}
			<br />
			{props.children}
		</div>
	);
};

App.propTypes = {
	children: PropTypes.element
};

export default App;
