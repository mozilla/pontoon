import * as React from 'react';
import { Localized } from '@fluent/react';

type Props = {
    signOut: () => void;
};

/*
 * Render a Sign Out link.
 */
export default class SignOut extends React.Component<Props> {
    signOut: () => void = () => {
        this.props.signOut();
    };

    render(): React.ReactElement<React.ElementType> {
        return (
            <Localized
                id='user-SignOut--sign-out'
                elems={{ glyph: <i className='fa fa-sign-out-alt fa-fw' /> }}
            >
                <button onClick={this.signOut}>
                    {'<glyph></glyph>Sign out'}
                </button>
            </Localized>
        );
    }
}
