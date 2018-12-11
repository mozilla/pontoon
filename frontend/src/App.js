/* @flow */

import React from 'react';
import { connect } from 'react-redux';

import './App.css';

import { Lightbox } from 'core/lightbox';
import * as locales from 'core/locales';
import { selectors as navSelectors } from 'core/navigation';
import { UserAutoUpdater } from 'core/user';
import { EntitiesList } from 'modules/entitieslist';
import { EntityDetails } from 'modules/entitydetails';
import { SearchBox } from 'modules/search';

import type { Navigation } from 'core/navigation';


type Props = {|
    parameters: Navigation,
|};

type InternalProps = {|
    ...Props,
    dispatch: Function,
|};


/**
 * Main entry point to the application. Will render the structure of the page.
 */
class App extends React.Component<InternalProps> {
    componentDidMount() {
        this.props.dispatch(locales.actions.get());
    }

    render() {
        return <div id="app">
            <UserAutoUpdater />
            <section className="panel-list">
                <SearchBox />
                <EntitiesList />
            </section>
            <section className="panel-content">
                <EntityDetails />
            </section>
            <Lightbox />
        </div>;
    }
}

const mapStateToProps = (state: Object): Props => {
    return {
        parameters: navSelectors.getNavigation(state),
    };
};

export default connect(mapStateToProps)(App);
