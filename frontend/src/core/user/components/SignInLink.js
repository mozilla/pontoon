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
    generateSignInURL() {
        const base = this.props.url;
        const startSign = base.match(/\?/) ? '&': '?';

        return (
            base +
            startSign +
            'next=' +
            window.location.pathname +
            window.location.search
        );
    }

    render() {
        return <a href={ this.generateSignInURL() }>
            { this.props.children }
        </a>;
    }
}
