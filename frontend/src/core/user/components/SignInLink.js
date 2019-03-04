/* @flow */

import * as React from 'react';


type Props = {|
    children?: React.Node,
    url: string,
|};


/*
 * Render a link to the Sign In process.
 */
export default class SignInLink extends React.Component<Props> {
    render() {
        return <a href={ this.props.url }>
            { this.props.children }
        </a>;
    }
}
