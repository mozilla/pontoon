/* @flow */

import * as React from 'react';
import { Localized } from 'fluent-react';

import './SignIn.css';

import SignInLink from './SignInLink';


/*
 * Render a Sign In link styled as a button.
 */
export default class SignIn extends React.Component<{}> {
    render() {
        return <span className='user-signin'>
            <Localized id='user-SignIn--sign-in'>
                <SignInLink>
                    Sign in
                </SignInLink>
            </Localized>
        </span>;
    }
}
