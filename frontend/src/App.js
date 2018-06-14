import React, { Component } from 'react';
import { connect } from 'react-redux';

import './App.css';

import { fetchEntitiesList } from './actions';

import EntitiesList from './EntitiesList';


class App extends Component {
    componentWillMount() {
        const { locale, project } = this.props.parameters;
        this.props.dispatch(fetchEntitiesList(locale, project));
    }

    selectEntity() {
        console.log('click');
    }

    render() {
        return (
            <EntitiesList entities={ this.props.entities } selectEntity={ this.selectEntity } />
        );
    }
}

const mapStateToProps = state => {
    return {
        parameters: state.parameters,
        entities: state.entities,
    };
};

export default connect(mapStateToProps)(App);
