/* @flow */

import React from 'react';
import { connect } from 'react-redux';

import navigation from 'core/navigation';
import type { State as NavState } from 'core/navigation';

import { get } from '../actions';
import { NAME } from '../constants';
import Entity from './Entity';

import type { Entities } from '../reducer';


type Props = {
    dispatch: Function,
    parameters: NavState,
    entities: Entities,
};

/**
 * Displays a list of entities and their current translation.
 *
 * This component will fetch entities when loaded, then displays those
 * entities. It interacts with `core/navigation` when an entity is selected.
 *
 */
class EntitiesList extends React.Component<Props> {
    componentWillMount() {
        const { locale, project, resource } = this.props.parameters;
        this.props.dispatch(get(locale, project, resource));
    }

    selectEntity = (e: SyntheticEvent<>) => {
        console.log('click');
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


const mapStateToProps = state => {
    return {
        parameters: state[navigation.constants.NAME],
        entities: state[NAME].entities,
    };
};

export default connect(mapStateToProps)(EntitiesList);
