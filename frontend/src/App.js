/* @flow */

import React from 'react';
import { connect } from 'react-redux';

import './App.css';

import * as l10n from 'core/l10n';
import { Lightbox } from 'core/lightbox';
import { WaveLoader } from 'core/loaders';
import * as locales from 'core/locales';
import { Navigation } from 'core/navigation';
import * as user from 'core/user';
import { EntitiesList } from 'modules/entitieslist';
import { EntityDetails } from 'modules/entitydetails';
import { SearchBox } from 'modules/search';

import type { L10nState } from 'core/l10n';
import type { LocalesState } from 'core/locales';
import type { UserState } from 'core/user';


const AppSwitcher = (props) => {
    if (!props.user || !props.user.isAuthenticated) {
        return null;
    }

    const currentURL = props.router.location.pathname + props.router.location.search;
    const target = '/toggle-use-translate-next/?next=' + currentURL;

    return <div className='options'>
        <a
            href={ target }
            title='Switch back to the current Translate app'
            className='toggle-translate-next'
        >
            Leave Translate.Next
        </a>
    </div>;
}


type Props = {|
    l10n: L10nState,
    locales: LocalesState,
    router: Object,
    user: UserState,
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
            <user.UserAutoUpdater />
            <header>
                { /* To be removed as part of bug 1527853. */ }
                <AppSwitcher router={ state.router } user={ state.user } />
                <Navigation />
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
        router: state.router,
        user: state[user.NAME],
    };
};

export default connect(mapStateToProps)(App);
