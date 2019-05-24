/* @flow */

import React from 'react';
import { connect } from 'react-redux';

import './App.css';

import * as l10n from 'core/l10n';
import { Lightbox } from 'core/lightbox';
import { WaveLoader } from 'core/loaders';
import * as locales from 'core/locales';
import * as navigation from 'core/navigation';
import * as notification from 'core/notification';
import * as project from 'core/project';
import { UserControls } from 'core/user';
import { EntitiesList } from 'modules/entitieslist';
import { EntityDetails } from 'modules/entitydetails';
import { ProjectInfo } from 'modules/projectinfo';
import { SearchBox } from 'modules/search';

import type { L10nState } from 'core/l10n';
import type { LocalesState } from 'core/locales';
import type { NavigationParams } from 'core/navigation';
import type { ProjectState } from 'core/project';


type Props = {|
    l10n: L10nState,
    locales: LocalesState,
    notification: notification.NotificationState,
    parameters: NavigationParams,
    project: ProjectState,
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
        this.props.dispatch(project.actions.get(this.props.parameters.project));
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
                <navigation.Navigation />
                <ProjectInfo
                    projectSlug={ state.parameters.project }
                    project={ state.project }
                />
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
        parameters: navigation.selectors.getNavigationParams(state),
        project: state[project.NAME],
    };
};

export default connect(mapStateToProps)(App);
