import React from 'react';
import ReactDOM from 'react-dom';

import { createStore, applyMiddleware } from 'redux';
import { Provider } from 'react-redux';
import thunkMiddleware from 'redux-thunk';
import { createLogger } from 'redux-logger';

import rootReducer from 'rootReducer';

import './index.css';
import App from './App';
import registerServiceWorker from './registerServiceWorker';


const loggerMiddleware = createLogger();

const createStoreWithMiddleware = applyMiddleware(
    thunkMiddleware,
    loggerMiddleware
)(createStore);

const store = createStoreWithMiddleware(rootReducer);

ReactDOM.render((
    <Provider store={ store }>
        <App />
    </Provider>
), document.getElementById('root'));
registerServiceWorker();
