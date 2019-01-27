/* @flow */

import React from 'react';
import { connect } from 'react-redux';

import './App.css';
import { L10nState } from 'core/l10n';
import { LocaleState } from 'core/locales';
import { Lightbox } from 'core/lightbox';
import * as locales from 'core/locales';
import { Navigation } from 'core/navigation';
import { UserAutoUpdater } from 'core/user';
import { EntitiesList } from 'modules/entitieslist';
import { EntityDetails } from 'modules/entitydetails';
import { SearchBox } from 'modules/search';
import { WaveLoader } from './core/loaders';

type Props = {|
    l10n: L10nState,
    locales: LocaleState,
|};

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
        const { l10n, locales } = this.props;
        const isLoading = l10n.fetching || locales.fetching;

        return <div id="app">
            <UserAutoUpdater />
            <header>
                <Navigation />
            </header>
            <WaveLoader isLoading={ isLoading }>
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

const mapStateToProps = (state: Object): Props => {
    const { l10n, locales } = state;

    return {
        l10n,
        locales,
    };
};

export default connect(mapStateToProps)(App);
