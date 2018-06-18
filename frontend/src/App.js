import React, { Component } from 'react';
import { connect } from 'react-redux';

import './App.css';

import { EntitiesList } from 'modules/entitieslist'


class App extends Component {
    render() {
        return (
            <EntitiesList />
        );
    }
}

const mapStateToProps = state => {
    return {
    };
};

export default connect(mapStateToProps)(App);
