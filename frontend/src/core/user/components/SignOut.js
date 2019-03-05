/* @flow */

import * as React from 'react';
import { Localized } from 'fluent-react';

import './SignOut.css';


type Props = {|
    signOut: () => void,
|};


/*
 * Render a Sign Out link.
 */
export default class SignOut extends React.Component<Props> {
    signOut = () => {
        this.props.signOut();
    }

    render() {
        return <span className='user-signout'>
            <Localized
                id='user-SignOut--sign-out'
                glyph={ <i className="fa fa-sign-out-alt fa-fw"></i> }
            >
                <button onClick={ this.signOut }>
                    { '<glyph></glyph> Sign out' }
                </button>
            </Localized>
        </span>;
    }
}
