/* @flow */

import * as React from 'react';
import { Localized } from 'fluent-react';

import './EntityNavigation.css';


type Props = {|
    +goToNextEntity: () => void,
    +goToPreviousEntity: () => void,
|};


/**
 * Component showing entity navigation toolbar.
 *
 * Shows next/previous buttons.
 */
export default class EntityNavigation extends React.Component<Props> {
    goToNextEntity = () => {
        this.props.goToNextEntity();
    }

    goToPreviousEntity = () => {
        this.props.goToPreviousEntity();
    }

    render(): React.Node {
        return <div className='entity-navigation clearfix'>
            <Localized
                id="entitynavigation-next"
                attrs={{ title: true }}
                glyph={
                    <i className="fa fa-chevron-down fa-lg"></i>
                }
            >
                <button
                    className="next"
                    title="Go To Next String (Alt + Down)"
                    onClick={ this.goToNextEntity }
                >
                    { '<glyph></glyph>Next' }
                </button>
            </Localized>
            <Localized
                id="entitynavigation-previous"
                attrs={{ title: true }}
                glyph={
                    <i className="fa fa-chevron-up fa-lg"></i>
                }
            >
                <button
                    className="previous"
                    title="Go To Previous String (Alt + Up)"
                    onClick={ this.goToPreviousEntity }
                >
                    { '<glyph></glyph>Previous' }
                </button>
            </Localized>
        </div>;
    }
}
