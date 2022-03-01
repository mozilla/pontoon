import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';

import { ConnectedRouter } from 'connected-react-router';
import TimeAgo from 'javascript-time-ago';
import en from 'javascript-time-ago/locale/en.json';

import './index.css';

import { AppLocalizationProvider } from '~/core/l10n';

import history from './historyInstance';
import store from './store';
import App from './App';

// TODO: Once we have support for more locales in Pontoon, we should
// make TimeAgo internationalized and initialize all locales here.
// See: https://www.npmjs.com/package/react-time-ago
TimeAgo.addLocale(en);

ReactDOM.render(
    <Provider store={store}>
        <ConnectedRouter history={history}>
            <AppLocalizationProvider>
                <App />
            </AppLocalizationProvider>
        </ConnectedRouter>
    </Provider>,
    document.getElementById('root'),
);
