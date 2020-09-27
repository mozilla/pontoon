/* @flow */

import * as React from 'react';
import { connect } from 'react-redux';

import './Lightbox.css';

import { NAME } from '..';
import { close } from '../actions';

import type { LightboxState } from '../reducer';

type Props = {|
    lightbox: LightboxState,
|};

type InternalProps = {|
    ...Props,
    dispatch: Function,
|};

/**
 * Shows an image on a grey background.
 *
 * Hides the UI behind a grey background and show a centered image.
 * Click or press a key to close.
 */
export class LightboxBase extends React.Component<InternalProps> {
    close = () => {
        this.props.dispatch(close());
    };

    closeOnKeys = (event: SyntheticKeyboardEvent<>) => {
        // On keys:
        //   - 13: Enter
        //   - 27: Escape
        //   - 32: Space
        if (
            event.keyCode === 13 ||
            event.keyCode === 27 ||
            event.keyCode === 32
        ) {
            this.close();
        }
    };

    componentDidMount() {
        // $FLOW_IGNORE (errors that I don't understand, no help from the Web)
        document.addEventListener('keydown', this.closeOnKeys);
    }

    componentWillUnmount() {
        // $FLOW_IGNORE (errors that I don't understand, no help from the Web)
        document.removeEventListener('keydown', this.closeOnKeys);
    }

    render() {
        const { lightbox } = this.props;

        if (!lightbox.isOpen) {
            return null;
        }

        return (
            <div className='lightbox' onClick={this.close}>
                <img src={lightbox.image} alt='' />
            </div>
        );
    }
}

const mapStateToProps = (state: Object): Props => {
    return {
        lightbox: state[NAME],
    };
};

export default connect(mapStateToProps)(LightboxBase);
