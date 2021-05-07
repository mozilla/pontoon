/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

import './EntityNavigation.css';

type Props = {|
    +copyLinkToClipboard: () => void,
    +goToNextEntity: () => void,
    +goToPreviousEntity: () => void,
|};

/**
 * Component showing entity navigation toolbar.
 *
 * Shows copy link and next/previous buttons.
 */
export default class EntityNavigation extends React.Component<Props> {
    componentDidMount() {
        document.addEventListener('keydown', this.handleShortcuts);
    }

    componentWillUnmount() {
        document.removeEventListener('keydown', this.handleShortcuts);
    }

    handleShortcuts: (event: KeyboardEvent) => void = (
        event: KeyboardEvent,
    ) => {
        const key = event.keyCode;

        // On Alt + Up, move to the previous entity.
        if (key === 38 && event.altKey && !event.ctrlKey && !event.shiftKey) {
            event.preventDefault();
            this.props.goToPreviousEntity();
        }

        // On Alt + Down, move to the next entity.
        if (key === 40 && event.altKey && !event.ctrlKey && !event.shiftKey) {
            event.preventDefault();
            this.props.goToNextEntity();
        }
    };

    render(): React.Node {
        return (
            <div className='entity-navigation clearfix'>
                <Localized
                    id='entitydetails-EntityNavigation--link'
                    attrs={{ title: true }}
                    elems={{ glyph: <i className='fa fa-link fa-lg' /> }}
                >
                    <button
                        className='link'
                        title='Copy Link to String'
                        onClick={this.props.copyLinkToClipboard}
                    >
                        {'<glyph></glyph>COPY LINK'}
                    </button>
                </Localized>
                <Localized
                    id='entitydetails-EntityNavigation--next'
                    attrs={{ title: true }}
                    elems={{
                        glyph: <i className='fa fa-chevron-down fa-lg' />,
                    }}
                >
                    <button
                        className='next'
                        title='Go To Next String (Alt + Down)'
                        onClick={this.props.goToNextEntity}
                    >
                        {'<glyph></glyph>NEXT'}
                    </button>
                </Localized>
                <Localized
                    id='entitydetails-EntityNavigation--previous'
                    attrs={{ title: true }}
                    elems={{ glyph: <i className='fa fa-chevron-up fa-lg' /> }}
                >
                    <button
                        className='previous'
                        title='Go To Previous String (Alt + Up)'
                        onClick={this.props.goToPreviousEntity}
                    >
                        {'<glyph></glyph>PREVIOUS'}
                    </button>
                </Localized>
            </div>
        );
    }
}
