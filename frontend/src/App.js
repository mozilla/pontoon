/* @flow */

import React from 'react';
import { connect } from 'react-redux';

import './App.css';

import * as l10n from 'core/l10n';
import { Lightbox } from 'core/lightbox';
import { WaveLoader } from 'core/loaders';
import * as locales from 'core/locales';
import { Navigation } from 'core/navigation';
import { NotificationPanel } from 'core/notification';
import { UserControls } from 'core/user';
import { EntitiesList } from 'modules/entitieslist';
import { EntityDetails } from 'modules/entitydetails';
import { SearchBox } from 'modules/search';

import type { L10nState } from 'core/l10n';
import type { LocalesState } from 'core/locales';


type Props = {|
    l10n: L10nState,
    locales: LocalesState,
|};

type InternalProps = {
    ...Props,
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
        const state = this.props;

        if (state.l10n.fetching || state.locales.fetching) {
            return <WaveLoader />;
        }

        return <div id="app">
            <header>
                <UserControls />
                <Navigation />
                <NotificationPanel />
            </header>
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
        l10n: state[l10n.NAME],
        locales: state[locales.NAME],
    };
};

export default connect(mapStateToProps)(App);
