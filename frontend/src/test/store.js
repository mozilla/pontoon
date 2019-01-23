/*
 * A redux store creator for our testing environment.
 *
 * Notably, this one doesn't have any logging, and supports an initialState.
 */

import { applyMiddleware, compose, createStore } from 'redux';
import thunkMiddleware from 'redux-thunk';
import { connectRouter, routerMiddleware } from 'connected-react-router';

import rootReducer from 'rootReducer';

import history from './history';


export function createReduxStore(initialState = {}) {
    return createStore(
        connectRouter(history)(rootReducer),
        initialState, // initial state
        compose(
            applyMiddleware(
                routerMiddleware(history),
                thunkMiddleware,
            )
        )
    );
}
