import React, { Component } from 'react';
import { connect } from 'react-redux';

import { NAME as NAVIGATION_NAME } from 'core/navigation';
import { actions, EntitiesList } from 'modules/entitieslist';


/**
 * Main entry point to the application. Will render the structure of the page.
 */
class App extends Component {
    componentDidMount() {
        const { locale, project, resource } = this.props.parameters;
        this.props.dispatch(actions.get(locale, project, resource));
    }

    render() {
        return (
            <EntitiesList />
        );
    }
}

const mapStateToProps = state => {
    return {
        parameters: state[NAVIGATION_NAME],
    };
};

export default connect(mapStateToProps)(App);
