/* @flow */

import * as React from 'react';


type Props = {|
    children?: React.Node,
|};


/*
 * Render a link to the Sign In process.
 */
export default class SignInLink extends React.Component<Props> {
    render() {
        return <a
            href='/accounts/fxa/login/?scope=profile%3Auid+profile%3Aemail+profile%3Adisplay_name'
        >
            { this.props.children }
        </a>;
    }
}
