import React, { Component } from 'react';
import { connect } from 'react-redux';

import './App.css';

import navigation from 'core/navigation';
import entitieslist, { EntitiesList } from 'modules/entitieslist';


class App extends Component {
    componentWillMount() {
        const { locale, project, resource } = this.props.parameters;
        this.props.dispatch(entitieslist.actions.get(locale, project, resource));
    }

    render() {
        return (
            <EntitiesList />
        );
    }
}

const mapStateToProps = state => {
    return {
        parameters: state[navigation.constants.NAME],
    };
};

export default connect(mapStateToProps)(App);
