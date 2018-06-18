import React from 'react';
import { connect } from 'react-redux';

import navigation from 'core/navigation';

import { get } from '../actions';
import { NAME } from '../constants';
import Entity from './Entity';


class EntitiesList extends React.Component {
    componentWillMount() {
        const { locale, project, resource } = this.props.parameters;
        this.props.dispatch(get(locale, project, resource));
    }

    selectEntity = e => {
        console.log('click');
    }

    render() {
        const { entities } = this.props;

        return (
            <ul className='entities'>
                { entities.map((entity, i) => {
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
