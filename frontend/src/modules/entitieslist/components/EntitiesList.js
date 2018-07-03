/* @flow */

import React from 'react';
import { connect } from 'react-redux';

import { NAME } from '../constants';
import Entity from './Entity';

import type { State, Entities } from '../reducer';


type Props = {
    entities: Entities,
};

/**
 * Displays a list of entities and their current translation.
 *
 * This component will fetch entities when loaded, then display those
 * entities. It interacts with `core/navigation` when an entity is selected.
 *
 */
export class EntitiesListBase extends React.Component<Props> {
    selectEntity = () => {
        // console.log('click');
    }

    render() {
        const { entities } = this.props;

        return (
            <ul className='entities'>
                { entities.map((entity: Object, i: number) => {
                    return <Entity
                        entity={ entity }
                        selectEntity={ this.selectEntity }
                        key={ i }
                    />;
                }) }
            </ul>
        );
    }
}


const mapStateToProps = (state: State): Props => {
    return {
        entities: state[NAME].entities,
    };
};

export default connect(mapStateToProps)(EntitiesListBase);
