import { applyMiddleware, compose, createStore } from 'redux';
import thunkMiddleware from 'redux-thunk';
import { createLogger } from 'redux-logger';
import { routerMiddleware } from 'connected-react-router';

import history from './historyInstance';
import createRootReducer from './rootReducer';

const middlewares = [routerMiddleware(history), thunkMiddleware];

// Log actions only in development.
if (process.env.NODE_ENV === 'development') {
    const loggerMiddleware = createLogger();
    middlewares.push(loggerMiddleware);
}

const store = createStore(
    createRootReducer(history),
    {}, // initial state
    compose(applyMiddleware(...middlewares)),
);

// Infer the `RootState` and `AppDispatch` types from the store itself
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export default store;
