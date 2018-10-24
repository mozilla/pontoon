/* @flow */

import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';
import { ConnectedRouter } from 'connected-react-router';

import './index.css';

import { AppLocalizationProvider } from 'core/l10n';

import history from './history';
import store from './store';
import App from './App';


ReactDOM.render(
    (
        <Provider store={ store }>
            <ConnectedRouter history={ history }>
                <AppLocalizationProvider>
                    <App />
                </AppLocalizationProvider>
            </ConnectedRouter>
        </Provider>
    ),
    // $FLOW_IGNORE: we know that the 'root' element exists.
    document.getElementById('root')
);
