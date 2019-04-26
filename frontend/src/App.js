/* @flow */

import React from 'react';
import { connect } from 'react-redux';

import './App.css';

import * as l10n from 'core/l10n';
import { Lightbox } from 'core/lightbox';
import { WaveLoader } from 'core/loaders';
import * as locales from 'core/locales';
import { Navigation } from 'core/navigation';
import * as notification from 'core/notification';
import { UserControls } from 'core/user';
import { EntitiesList } from 'modules/entitieslist';
import { EntityDetails } from 'modules/entitydetails';
import { SearchBox } from 'modules/search';

import type { L10nState } from 'core/l10n';
import type { LocalesState } from 'core/locales';


type Props = {|
    l10n: L10nState,
    locales: LocalesState,
    notification: notification.NotificationState,
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

    componentDidUpdate(prevProps: InternalProps) {
        // If there's a notification in the DOM, passed by django, show it.
        // Note that we only show it once, and only when the UI has already
        // been rendered, to make sure users do see it.
        if (
            !this.props.l10n.fetching &&
            !this.props.locales.fetching &&
            (prevProps.l10n.fetching ||
            prevProps.locales.fetching)
        ) {
            let notifications = [];
            const rootElt = document.getElementById('root');
            if (rootElt) {
                notifications = JSON.parse(rootElt.dataset.notifications);
            }

            if (notifications.length) {
                // Our notification system only supports showing one notification
                // for the moment, so we only add the first notification here.
                const notif = notifications[0];
                this.props.dispatch(notification.actions.addRaw(notif.content, notif.type));
            }
        }
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
                <notification.NotificationPanel notification={ state.notification } />
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
        notification: state[notification.NAME],
    };
};

export default connect(mapStateToProps)(App);
