/* @flow */

import * as React from 'react';

import './Lightbox.css';


type Props = {|
    image: string,
    close: Function,
|};


/**
 * Shows an image on a grey background.
 *
 * Hides the UI behind a grey background and show a centered image.
 * Click or press a key to close.
 */
export default class Lightbox extends React.Component<Props> {
    closeOnKeys = (event: SyntheticKeyboardEvent<>) => {
        // On keys:
        //   - 27: Escape
        //   - 32: Space
        //   - 13: Enter
        if (event.keyCode === 27 || event.keyCode === 32 || event.keyCode === 13) {
            this.props.close();
        }
    }

    componentDidMount() {
        // $FLOW_IGNORE (errors that I don't understand, no help from the Web)
        document.addEventListener('keydown', this.closeOnKeys);
    }

    componentWillUnmount() {
        // $FLOW_IGNORE (errors that I don't understand, no help from the Web)
        document.removeEventListener('keydown', this.closeOnKeys);
    }

    render() {
        const { image, close } = this.props;

        return <div className="lightbox" onClick={ close }>
            <img src={ image } alt="" />
        </div>
    }
}
