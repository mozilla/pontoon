/* @flow */

import React from 'react';
import { connect } from 'react-redux';
import { push } from 'connected-react-router';

import './EntitiesList.css';

import { selectors as navSelectors } from 'core/navigation';
import type { Navigation } from 'core/navigation';

import { NAME } from '..';
import Entity from './Entity';

import type { State, Entities, DbEntity } from '../reducer';


type Props = {|
    entities: Entities,
    parameters: Navigation,
|};

type InternalProps = {|
    ...Props,
    dispatch: Function,
|};

/**
 * Displays a list of entities and their current translation.
 *
 * This component will fetch entities when loaded, then display those
 * entities. It interacts with `core/navigation` when an entity is selected.
 *
 */
export class EntitiesListBase extends React.Component<InternalProps> {
    selectEntity = (entity: DbEntity) => {
        this.props.dispatch(push(`?string=${entity.pk}`));
    }

    render() {
        const { entities } = this.props;
        const selectedEntity = this.props.parameters.entity;

        return (
            <ul className='entities'>
                { entities.map((entity: Object, i: number) => {
                    return <Entity
                        entity={ entity }
                        selectEntity={ this.selectEntity }
                        key={ i }
                        selected={ entity.pk === selectedEntity }
                    />;
                }) }
            </ul>
        );
    }
}


const mapStateToProps = (state: State): Props => {
    return {
        entities: state[NAME].entities,
        parameters: navSelectors.getNavigation(state),
    };
};

export default connect(mapStateToProps)(EntitiesListBase);
