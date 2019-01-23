import { applyMiddleware, compose, createStore } from 'redux';
import thunkMiddleware from 'redux-thunk';
import { createLogger } from 'redux-logger';
import { connectRouter, routerMiddleware } from 'connected-react-router';

import history from './history';
import rootReducer from './rootReducer';


const loggerMiddleware = createLogger();

export default createStore(
    connectRouter(history)(rootReducer),
    {}, // initial state
    compose(
        applyMiddleware(
            routerMiddleware(history),
            thunkMiddleware,
            loggerMiddleware,
        )
    )
);
