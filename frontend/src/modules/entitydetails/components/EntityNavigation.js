/* @flow */

import * as React from 'react';
import { Localized } from 'fluent-react';

import './EntityNavigation.css';

import type { DbEntity } from 'modules/entitieslist';


type Props = {|
    +entity: DbEntity,
|};


/**
 * Component showing entity navigation toolbar.
 *
 * Shows next/previous buttons.
 */
export default class EntityNavigation extends React.Component<Props> {
    goToNextEntity = (entity: DbEntity) => {
        console.log("foo");
    }

    goToPreviousEntity = (entity: DbEntity) => {
        console.log("bar");
    }

    render(): React.Node {
        const { entity } = this.props;

        return <div className='entity-navigation clearfix'>
            <Localized
                id="entitynavigation-next"
                attrs={{ title: true }}
                glyph={
                    <i className="fa fa-chevron-down fa-lg"></i>
                }
            >
                <button
                    id="next"
                    title="Go To Next String (Alt + Down)"
                    onClick={ this.goToNextEntity(entity) }
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
                    id="previous"
                    title="Go To Previous String (Alt + Up)"
                    onClick={ this.goToPreviousEntity(entity) }
                >
                    { '<glyph></glyph>Previous' }
                </button>
            </Localized>
        </div>;
    }
}
