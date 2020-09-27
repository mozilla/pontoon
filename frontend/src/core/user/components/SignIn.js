/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

import './SignIn.css';

import SignInLink from './SignInLink';

type Props = {|
    url: string,
|};

/*
 * Render a Sign In link styled as a button.
 */
export default class SignIn extends React.Component<Props> {
    render() {
        return (
            <span className='user-signin'>
                <Localized id='user-SignIn--sign-in'>
                    <SignInLink url={this.props.url}>Sign in</SignInLink>
                </Localized>
            </span>
        );
    }
}
