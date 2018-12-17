/* @flow */

import React from 'react';
import { connect } from 'react-redux';

import './App.css';

import { Lightbox } from 'core/lightbox';
import * as locales from 'core/locales';
import { Navigation } from 'core/navigation';
import { UserAutoUpdater } from 'core/user';
import { EntitiesList } from 'modules/entitieslist';
import { EntityDetails } from 'modules/entitydetails';
import { SearchBox } from 'modules/search';
import { WaveLoader } from './core/loaders';


type InternalProps = {
    dispatch: Function,
};


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
            <header>
                <Navigation />
            </header>
            <WaveLoader>
                <section className="panel-list">
                    <SearchBox />
                    <EntitiesList />
                </section>
                <section className="panel-content">
                    <EntityDetails />
                </section>
            </WaveLoader>
            <Lightbox />
        </div>;
    }
}

export default connect()(App);
