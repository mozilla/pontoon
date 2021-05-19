import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';

import { ConnectedRouter } from 'connected-react-router';
// javascript-time-ago is installed automatically with react-time-ago
// See: https://www.npmjs.com/package/react-time-ago
import JavascriptTimeAgo from 'javascript-time-ago';
import en from 'javascript-time-ago/locale/en';

import './index.css';

import { AppLocalizationProvider } from 'core/l10n';

import history from './historyInstance';
import store from './store';
import App from './App';

// TODO: Once we have support for more locales in Pontoon, we should
// make TimeAgo internationalized and initialize all locales here.
// See: https://www.npmjs.com/package/react-time-ago
JavascriptTimeAgo.locale(en);

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
