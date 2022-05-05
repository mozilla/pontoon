import { useLocalization } from '@fluent/react';
import React, { useContext, useEffect, useState } from 'react';

import './App.css';

import { initLocale, Locale, updateLocale } from './context/locale';
import { Location } from './context/location';

import { WaveLoader } from './core/loaders';
import { NAME as NOTIFICATION, NotificationPanel } from './core/notification';
import { addRawNotification } from './core/notification/actions';
import { getProject } from './core/project/actions';
import { getResource } from './core/resource/actions';
import { UserControls } from './core/user';
import { getUsers } from './core/user/actions';

import { useAppDispatch, useAppSelector } from './hooks';

import { AddonPromotion } from './modules/addonpromotion/components/AddonPromotion';
import { BatchActions } from './modules/batchactions/components/BatchActions';
import { useBatchactions } from './modules/batchactions/hooks';
import { EntitiesList } from './modules/entitieslist';
import { EntityDetails } from './modules/entitydetails';
import { InteractiveTour } from './modules/interactivetour/components/InteractiveTour';
import { Navigation } from './modules/navbar';
import { ProjectInfo } from './modules/projectinfo/components/ProjectInfo';
import { ResourceProgress } from './modules/resourceprogress';
import { SearchBox } from './modules/search';

/**
 * Main entry point to the application. Will render the structure of the page.
 */
export function App() {
  const dispatch = useAppDispatch();
  const location = useContext(Location);
  const batchactions = useBatchactions();
  const notification = useAppSelector((state) => state[NOTIFICATION]);
  const { l10n } = useLocalization();

  const [locale, _setLocale] = useState(initLocale((next) => _setLocale(next)));

  const l10nReady = !!l10n.parseMarkup;
  const allProjects = location.project === 'all-projects';

  useEffect(() => {
    // If there's a notification in the DOM, passed by django, show it.
    // Note that we only show it once, and only when the UI has already
    // been rendered, to make sure users do see it.
    if (l10nReady && !locale.fetching) {
      let notifications = [];
      const rootElt = document.getElementById('root');
      if (rootElt?.dataset.notifications) {
        notifications = JSON.parse(rootElt.dataset.notifications);
      }

      if (notifications.length) {
        // Our notification system only supports showing one notification
        // for the moment, so we only add the first notification here.
        const notif = notifications[0];
        dispatch(addRawNotification(notif.content, notif.type));
      }
    }
  }, [l10nReady, locale.fetching]);

  useEffect(() => {
    updateLocale(locale, location.locale);
    dispatch(getProject(location.project));
    dispatch(getUsers());

    // Load resources, unless we're in the All Projects view
    if (!allProjects) {
      dispatch(getResource(location.locale, location.project));
    }
  }, []);

  if (!l10nReady || locale.fetching) {
    return <WaveLoader />;
  }

  return (
    <Locale.Provider value={locale}>
      <div id='app'>
        <AddonPromotion />
        <header>
          <Navigation />
          <ResourceProgress />
          {allProjects ? null : <ProjectInfo />}
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
        <InteractiveTour />
      </div>
    </Locale.Provider>
  );
}
