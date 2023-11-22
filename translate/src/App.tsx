import { useLocalization } from '@fluent/react';
import classNames from 'classnames';
import React, { useContext, useEffect, useState } from 'react';

import './App.css';

import { EntitiesList as EntitiesListContext } from './context/EntitiesList';
import { EntityViewProvider } from '~/context/EntityView';
import { initLocale, Locale, updateLocale } from './context/Locale';
import { Location } from './context/Location';
import { MentionUsersProvider } from './context/MentionUsers';
import { NotificationProvider } from './context/Notification';
import { ThemeProvider } from './context/Theme';

import { WaveLoader } from './modules/loaders';
import { NotificationPanel } from './modules/notification/components/NotificationPanel';
import { getProject } from './modules/project/actions';
import { getResource } from './modules/resource/actions';
import { UserControls } from './modules/user/components/UserControls';

import { useAppDispatch } from './hooks';

import { AddonPromotion } from './modules/addonpromotion/components/AddonPromotion';
import { BatchActions } from './modules/batchactions/components/BatchActions';
import { useBatchactions } from './modules/batchactions/hooks';
import { EntitiesList } from './modules/entitieslist';
import { Entity } from './modules/entitydetails/components/Entity';
import { InteractiveTour } from './modules/interactivetour/components/InteractiveTour';
import { Navigation } from './modules/navbar/components/Navigation';
import { ProjectInfo } from './modules/projectinfo/components/ProjectInfo';
import { ResourceProgress } from './modules/resourceprogress';
import { SearchBox } from './modules/search/components/SearchBox';

/**
 * Main entry point to the application. Will render the structure of the page.
 */
export function App() {
  const dispatch = useAppDispatch();
  const location = useContext(Location);
  const batchactions = useBatchactions();
  const { visible } = useContext(EntitiesListContext);
  const { l10n } = useLocalization();

  const [locale, _setLocale] = useState(initLocale((next) => _setLocale(next)));

  const l10nReady = !!l10n.parseMarkup;
  const allProjects = location.project === 'all-projects';

  useEffect(() => {
    updateLocale(locale, location.locale);
  }, []);

  useEffect(() => {
    dispatch(getProject(location.project));
    if (!allProjects) {
      dispatch(getResource(location.locale, location.project));
    }
  }, [location.locale, location.project]);

  if (!l10nReady || locale.fetching) {
    return <WaveLoader />;
  }

  return (
    <Locale.Provider value={locale}>
      <NotificationProvider>
        <ThemeProvider>
          <MentionUsersProvider>
            <EntityViewProvider>
              <div id='app'>
                <AddonPromotion />
                <header>
                  <Navigation />
                  <ResourceProgress />
                  {allProjects ? null : <ProjectInfo />}
                  <NotificationPanel />
                  <UserControls />
                </header>
                <section
                  className={classNames(
                    'main-content',
                    visible ? 'entities-list' : '',
                  )}
                >
                  <section className='panel-list'>
                    <SearchBox />
                    <EntitiesList />
                  </section>
                  <section className='panel-content'>
                    {batchactions.entities.length === 0 ? (
                      <Entity />
                    ) : (
                      <BatchActions />
                    )}
                  </section>
                </section>
                <InteractiveTour />
              </div>
            </EntityViewProvider>
          </MentionUsersProvider>
        </ThemeProvider>
      </NotificationProvider>
    </Locale.Provider>
  );
}
