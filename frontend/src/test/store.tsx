/*
 * A redux store creator for our testing environment.
 *
 * Notably, this one doesn't have any logging, and supports an initialState.
 */

import React from 'react';
import { applyMiddleware, compose, createStore } from 'redux';
import { Provider } from 'react-redux';
import thunkMiddleware from 'redux-thunk';
import { mount } from 'enzyme';
import { ConnectedRouter, routerMiddleware } from 'connected-react-router';
import { createMemoryHistory } from 'history';

import * as user from 'core/user';

import createRootReducer from 'rootReducer';

const history = createMemoryHistory({
    initialEntries: ['/kg/firefox/all-resources/'],
});

export function createReduxStore(initialState = {}) {
    return createStore(
        createRootReducer(history),
        initialState,
        compose(applyMiddleware(routerMiddleware(history), thunkMiddleware)),
    );
}

export function mountComponentWithStore(Component, store, props = {}) {
    return mount(
        <Provider store={store}>
            {/* `noInitialPop` is required to omit an initial navigation dispatch
            from the router, which could have side-effects like resetting some
            initial state passed to the root reducer factory function.*/}
            <ConnectedRouter history={history} noInitialPop>
                <Component {...props} />
            </ConnectedRouter>
        </Provider>,
    );
}

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
