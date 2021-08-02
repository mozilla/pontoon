import React from 'react';
import { connect } from 'react-redux';

import './App.css';

import * as l10n from 'core/l10n';
import { Lightbox } from 'core/lightbox';
import { WaveLoader } from 'core/loaders';
import * as locale from 'core/locale';
import * as navigation from 'core/navigation';
import * as notification from 'core/notification';
import * as project from 'core/project';
import * as resource from 'core/resource';
import * as stats from 'core/stats';
import * as user from 'core/user';
import { AddonPromotion } from 'modules/addonpromotion';
import * as batchactions from 'modules/batchactions';
import { UserControls } from 'core/user';
import { BatchActions } from 'modules/batchactions';
import { EntitiesList } from 'modules/entitieslist';
import { EntityDetails } from 'modules/entitydetails';
import { Navigation } from 'modules/navbar';
import { ProjectInfo } from 'modules/projectinfo';
import { ResourceProgress } from 'modules/resourceprogress';
import { SearchBox } from 'modules/search';
import { InteractiveTour } from 'modules/interactivetour';

import type { BatchActionsState } from 'modules/batchactions';
import type { L10nState } from 'core/l10n';
import type { LocaleState } from 'core/locale';
import type { NavigationParams } from 'core/navigation';
import type { ProjectState } from 'core/project';
import type { Stats } from 'core/stats';
import { AppState } from 'rootReducer';

type Props = {
    batchactions: BatchActionsState;
    l10n: L10nState;
    locale: LocaleState;
    notification: notification.NotificationState;
    parameters: NavigationParams;
    project: ProjectState;
    stats: Stats;
};

type InternalProps = Props & {
    dispatch: (...args: Array<any>) => any;
};

/**
 * Main entry point to the application. Will render the structure of the page.
 */
class App extends React.Component<InternalProps> {
    componentDidMount() {
        const { parameters } = this.props;

        this.props.dispatch(locale.actions.get(parameters.locale));
        this.props.dispatch(project.actions.get(parameters.project));
        this.props.dispatch(user.actions.getUsers());

        // Load resources, unless we're in the All Projects view
        if (parameters.project !== 'all-projects') {
            this.props.dispatch(
                resource.actions.get(parameters.locale, parameters.project),
            );
        }
    }

    componentDidUpdate(prevProps: InternalProps) {
        // If there's a notification in the DOM, passed by django, show it.
        // Note that we only show it once, and only when the UI has already
        // been rendered, to make sure users do see it.
        if (
            !this.props.l10n.fetching &&
            !this.props.locale.fetching &&
            (prevProps.l10n.fetching || prevProps.locale.fetching)
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
                this.props.dispatch(
                    notification.actions.addRaw(notif.content, notif.type),
                );
            }
        }
    }

    render() {
        const state = this.props;

        if (state.l10n.fetching || state.locale.fetching) {
            return <WaveLoader />;
        }

        return (
            <div id='app'>
                <AddonPromotion />
                <header>
                    <Navigation />
                    <ResourceProgress
                        stats={state.stats}
                        parameters={state.parameters}
                    />
                    <ProjectInfo
                        projectSlug={state.parameters.project}
                        project={state.project}
                    />
                    <notification.NotificationPanel
                        notification={state.notification}
                    />
                    <UserControls />
                </header>
                <section className='main-content'>
                    <section className='panel-list'>
                        <SearchBox />
                        <EntitiesList />
                    </section>
                    <section className='panel-content'>
                        {state.batchactions.entities.length === 0 ? (
                            <EntityDetails />
                        ) : (
                            <BatchActions />
                        )}
                    </section>
                </section>
                <Lightbox />
                <InteractiveTour />
            </div>
        );
    }
}

const mapStateToProps = (state: AppState): Props => {
    return {
        batchactions: state[batchactions.NAME],
        l10n: state[l10n.NAME],
        locale: state[locale.NAME],
        notification: state[notification.NAME],
        parameters: navigation.selectors.getNavigationParams(state),
        project: state[project.NAME],
        stats: state[stats.NAME],
    };
};

export default connect(mapStateToProps)(App);
