import { applyMiddleware, compose, createStore } from 'redux';
import thunkMiddleware from 'redux-thunk';
import { createLogger } from 'redux-logger';
import { routerMiddleware } from 'connected-react-router';

import history from './history';
import createRootReducer from './rootReducer';

const middlewares = [routerMiddleware(history), thunkMiddleware];

// Log actions only in development.
if (process.env.NODE_ENV === 'development') {
    const loggerMiddleware = createLogger();
    middlewares.push(loggerMiddleware);
}

export default createStore(
    createRootReducer(history),
    {}, // initial state
    compose(applyMiddleware(...middlewares)),
);
