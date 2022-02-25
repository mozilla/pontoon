import React, { useEffect, useRef, useState } from 'react';
import { connect } from 'react-redux';

import { initLocale, Locale, updateLocale } from './context/locale';

import { L10nState, NAME as L10N } from './core/l10n';
import { Lightbox } from './core/lightbox';
import { WaveLoader } from './core/loaders';
import type { NavigationParams } from './core/navigation';
import { getNavigationParams } from './core/navigation/selectors';
import {
  NAME as NOTIFICATION,
  NotificationPanel,
  NotificationState,
} from './core/notification';
import { addRaw } from './core/notification/actions';
import { NAME as PROJECT, ProjectState } from './core/project';
import { get as getProject } from './core/project/actions';
import { get as getResource } from './core/resource/actions';
import { NAME as STATS, Stats } from './core/stats';
import { UserControls } from './core/user';
import { getUsers } from './core/user/actions';

import { AddonPromotion } from './modules/addonpromotion';
import {
  BatchActions,
  BatchActionsState,
  NAME as BATCHACTIONS,
} from './modules/batchactions';
import { EntitiesList } from './modules/entitieslist';
import { EntityDetails } from './modules/entitydetails';
import { InteractiveTour } from './modules/interactivetour';
import { Navigation } from './modules/navbar';
import { ProjectInfo } from './modules/projectinfo';
import { ResourceProgress } from './modules/resourceprogress';
import { SearchBox } from './modules/search';

import { AppDispatch, RootState } from './store';

import './App.css';

type Props = {
  batchactions: BatchActionsState;
  l10n: L10nState;
  notification: NotificationState;
  parameters: NavigationParams;
  project: ProjectState;
  stats: Stats;
};

type InternalProps = Props & {
  dispatch: AppDispatch;
};

/**
 * Main entry point to the application. Will render the structure of the page.
 */
function App({
  batchactions,
  dispatch,
  l10n,
  notification,
  parameters,
  project,
  stats,
}: InternalProps) {
  const mounted = useRef(false);
  const [locale, _setLocale] = useState(initLocale((next) => _setLocale(next)));

  useEffect(() => {
    // If there's a notification in the DOM, passed by django, show it.
    // Note that we only show it once, and only when the UI has already
    // been rendered, to make sure users do see it.
    if (mounted.current && !l10n.fetching && !locale.fetching) {
      let notifications = [];
      const rootElt = document.getElementById('root');
      if (rootElt?.dataset.notifications) {
        notifications = JSON.parse(rootElt.dataset.notifications);
      }

      if (notifications.length) {
        // Our notification system only supports showing one notification
        // for the moment, so we only add the first notification here.
        const notif = notifications[0];
        dispatch(addRaw(notif.content, notif.type));
      }
    }
  }, [l10n.fetching, locale.fetching]);

  useEffect(() => {
    updateLocale(locale, parameters.locale);
    dispatch(getProject(parameters.project));
    dispatch(getUsers());

    // Load resources, unless we're in the All Projects view
    if (parameters.project !== 'all-projects') {
      dispatch(getResource(parameters.locale, parameters.project));
    }
    mounted.current = true;
  }, []);

  if (l10n.fetching || locale.fetching) {
    return <WaveLoader />;
  }

  return (
    <Locale.Provider value={locale}>
      <div id='app'>
        <AddonPromotion />
        <header>
          <Navigation />
          <ResourceProgress stats={stats} parameters={parameters} />
          <ProjectInfo projectSlug={parameters.project} project={project} />
          <NotificationPanel notification={notification} />
          <UserControls />
        </header>
        <section className='main-content'>
          <section className='panel-list'>
            <SearchBox />
            <EntitiesList />
          </section>
          <section className='panel-content'>
            {batchactions.entities.length === 0 ? (
              <EntityDetails />
            ) : (
              <BatchActions />
            )}
          </section>
        </section>
        <Lightbox />
        <InteractiveTour />
      </div>
    </Locale.Provider>
  );
}

const mapStateToProps = (state: RootState): Props => {
  return {
    batchactions: state[BATCHACTIONS],
    l10n: state[L10N],
    notification: state[NOTIFICATION],
    parameters: getNavigationParams(state),
    project: state[PROJECT],
    stats: state[STATS],
  };
};

export default connect(mapStateToProps)(App);
