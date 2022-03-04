/*
 * A redux store creator for our testing environment.
 *
 * Notably, this one doesn't have any logging, and supports an initialState.
 */

import React from 'react';
import { configureStore } from '@reduxjs/toolkit';
import { Provider } from 'react-redux';
import { mount } from 'enzyme';
import { ConnectedRouter, routerMiddleware } from 'connected-react-router';
import { createMemoryHistory } from 'history';

import { LocationProvider } from '~/context/location';
import * as user from '~/core/user';
import createRootReducer from '~/rootReducer';

const HISTORY = createMemoryHistory({
  initialEntries: ['/kg/firefox/all-resources/'],
});

export const createReduxStore = (initialState = {}, history = HISTORY) =>
  configureStore({
    reducer: createRootReducer(history),
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware({ serializableCheck: false }).prepend(
        routerMiddleware(history),
      ),
    preloadedState: initialState,
  });

export const mountComponentWithStore = (
  Component,
  store,
  props = {},
  history = HISTORY,
) =>
  mount(
    <Provider store={store}>
      {/* `noInitialPop` is required to omit an initial navigation dispatch
            from the router, which could have side-effects like resetting some
            initial state passed to the root reducer factory function.*/}
      <ConnectedRouter history={history} noInitialPop>
        <LocationProvider history={history}>
          <Component {...props} />
        </LocationProvider>
      </ConnectedRouter>
    </Provider>,
  );

export function createDefaultUser(store, initial = {}) {
  const userData = {
    settings: {
      force_suggestions: false,
    },
    username: 'Franck',
    is_authenticated: true,
    manager_for_locales: ['kg'],
    translator_for_locales: [],
    translator_for_projects: {},
  };

  const data = {
    ...userData,
    ...initial,
  };

  store.dispatch(user.actions.update(data));
}
