import { push } from 'connected-react-router';
import React, { useCallback, useEffect, useRef } from 'react';

import { LocaleState, NAME as LOCALE } from '~/core/locale';
import type { NavigationParams } from '~/core/navigation';
import { getNavigationParams } from '~/core/navigation/selectors';
import { NAME as PROJECT, ProjectMenu, ProjectState } from '~/core/project';
import { get as getProject } from '~/core/project/actions';
import {
  NAME as RESOURCE,
  ResourceMenu,
  ResourcesState,
} from '~/core/resource';
import { get as getResource } from '~/core/resource/actions';
import { AppStore, useAppDispatch, useAppSelector, useAppStore } from '~/hooks';
import { NAME as UNSAVED_CHANGES } from '~/modules/unsavedchanges';
import { check as checkUnsavedChanges } from '~/modules/unsavedchanges/actions';
import type { AppDispatch } from '~/store';

import './Navigation.css';

type Props = {
  locale: LocaleState;
  parameters: NavigationParams;
  project: ProjectState;
  resources: ResourcesState;
};

type InternalProps = Props & {
  dispatch: AppDispatch;
  store: AppStore;
};

/**
 * Render a breadcrumb-like navigation bar.
 *
 * Allows to exit the Translate app to go back to team or project dashboards.
 */
export function NavigationBase({
  dispatch,
  locale,
  parameters,
  project,
  resources,
  store,
}: InternalProps): React.ReactElement<'nav'> | null {
  useEffect(() => {
    if (locale?.name && project?.name)
      document.title = `${locale.name} (${locale.code}) · ${project.name}`;
  }, [locale, project]);

  const mounted = useRef(false);
  useEffect(() => {
    if (mounted.current) {
      dispatch(getProject(parameters.project));

      // Load resources, unless we're in the All Projects view
      if (parameters.project !== 'all-projects') {
        dispatch(getResource(parameters.locale, parameters.project));
      }
    } else mounted.current = true;
  }, [dispatch, parameters.project]);

  const navigateToPath = useCallback(
    (path: string) => {
      const state = store.getState();
      const { exist, ignored } = state[UNSAVED_CHANGES];
      dispatch(
        checkUnsavedChanges(exist, ignored, () => {
          dispatch(push(path));
        }),
      );
    },
    [dispatch, store],
  );

  if (!locale) {
    return null;
  }

  return (
    <nav className='navigation'>
      <ul>
        <li>
          <a href='/'>
            <img
              src='/static/img/logo.svg'
              width='32'
              height='32'
              alt='Pontoon logo'
            />
          </a>
        </li>
        <li>
          <a href={`/${locale.code}/`}>
            {locale.name}
            <span className='locale-code'>{locale.code}</span>
          </a>
        </li>
        <ProjectMenu
          locale={locale}
          parameters={parameters}
          project={project}
          navigateToPath={navigateToPath}
        />
        <ResourceMenu
          parameters={parameters}
          resources={resources}
          navigateToPath={navigateToPath}
        />
      </ul>
    </nav>
  );
}

export default function Navigation(): React.ReactElement<
  typeof NavigationBase
> {
  const state = {
    locale: useAppSelector((state) => state[LOCALE]),
    parameters: useAppSelector(getNavigationParams),
    project: useAppSelector((state) => state[PROJECT]),
    resources: useAppSelector((state) => state[RESOURCE]),
  };

  return (
    <NavigationBase
      {...state}
      dispatch={useAppDispatch()}
      store={useAppStore()}
    />
  );
}
