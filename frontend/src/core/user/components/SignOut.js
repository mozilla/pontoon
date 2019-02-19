/* @flow */

import * as React from 'react';
import { Localized } from 'fluent-react';

import './SignOut.css';


/*
 * Render a Sign Out link.
 */
export default class SignOut extends React.Component<{}> {
    render() {
        return <span className='user-signout'>
            <Localized
                id='user-SignOut--sign-out'
                glyph={ <i className="fa fa-sign-out-alt fa-fw"></i> }
            >
                <a href='/accounts/logout/'>
                    { '<glyph></glyph> Sign out' }
                </a>
            </Localized>
        </span>;
    }
}
