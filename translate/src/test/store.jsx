/*
 * A redux store creator for our testing environment.
 *
 * Notably, this one doesn't have any logging, and supports an initialState.
 */

import React from 'react';
import { configureStore } from '@reduxjs/toolkit';
import { Provider } from 'react-redux';
import { createMemoryHistory } from 'history';

import { LocationProvider } from '~/context/Location';
import { UPDATE } from '~/modules/user/actions';
import { reducer } from '~/rootReducer';

import { MockLocalizationProvider } from './utils';
import { render } from '@testing-library/react';

const HISTORY = createMemoryHistory({
  initialEntries: ['/kg/firefox/all-resources/'],
});

export const createReduxStore = (initialState = {}) =>
  configureStore({
    reducer,
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware({ serializableCheck: false }),
    preloadedState: initialState,
  });

export const MockStore = ({ children, store, history = HISTORY, resource }) => (
  <Provider store={store}>
    <LocationProvider history={history}>
      <MockLocalizationProvider resource={resource}>
        {children}
      </MockLocalizationProvider>
    </LocationProvider>
  </Provider>
);

export const mountComponentWithStore = (
  Component,
  store,
  props = {},
  history,
  resource,
) =>
  render(
    <MockStore store={store} history={history} resource={resource}>
      <Component {...props} />
    </MockStore>,
  );

export function createDefaultUser(store, initial = {}) {
  const data = {
    settings: { force_suggestions: false },
    username: 'Franck',
    is_authenticated: true,
    can_manage_locales: ['kg'],
    can_translate_locales: [],
    translator_for_projects: {},
    ...initial,
  };
  store.dispatch({ type: UPDATE, data });
}
