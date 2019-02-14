/* @flow */

import React from 'react';
import { connect } from 'react-redux';

import './App.css';

import { NAME as L10N_NAME } from 'core/l10n';
import { NAME as LOCALES_NAME } from 'core/locales';
import { Lightbox } from 'core/lightbox';
import { WaveLoader } from 'core/loaders';
import * as locales from 'core/locales';
import { Navigation } from 'core/navigation';
import { UserAutoUpdater } from 'core/user';
import { EntitiesList } from 'modules/entitieslist';
import { EntityDetails } from 'modules/entitydetails';
import { SearchBox } from 'modules/search';

import type { L10nState } from 'core/l10n';
import type { LocalesState } from 'core/locales';


const AppSwitcher = (props) => {
    const { router } = props;

    const currentURL = router.location.pathname + router.location.search;
    const target = '/toggle-use-translate-next/?next=' + currentURL;

    return <div className='options'>
        <a
            href={ target }
            title='Switch back to the current Translate app'
        >
            Cancel Translate.Next
        </a>
    </div>;
}


type Props = {|
    l10n: L10nState,
    locales: LocalesState,
    router: Object,
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
        const { l10n, locales, router } = this.props;

        if (l10n.fetching || locales.fetching) {
            return <WaveLoader />;
        }

        return <div id="app">
            <UserAutoUpdater />
            <header>
                { /* To be removed as part of bug 1527853. */ }
                <AppSwitcher router={ router } />
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
        l10n: state[L10N_NAME],
        locales: state[LOCALES_NAME],
        router: state.router,
    };
};

export default connect(mapStateToProps)(App);
