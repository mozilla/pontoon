import TimeAgo from 'javascript-time-ago';
import en from 'javascript-time-ago/locale/en.json';
import React from 'react';
import { render } from 'react-dom';
import { Provider } from 'react-redux';

import './index.css';
import { App } from './App';
import { LocationProvider } from './context/Location';
import { UnsavedChangesProvider } from './context/UnsavedChanges';
import { AppLocalizationProvider } from './modules/l10n/components/AppLocalizationProvider';
import { history } from './historyInstance';
import { store } from './store';

// TODO: Once we have support for more locales in Pontoon, we should
// make TimeAgo internationalized and initialize all locales here.
// See: https://www.npmjs.com/package/react-time-ago
TimeAgo.addLocale(en);

render(
  <Provider store={store}>
    <LocationProvider history={history}>
      <AppLocalizationProvider>
        <UnsavedChangesProvider>
          <App />
        </UnsavedChangesProvider>
      </AppLocalizationProvider>
    </LocationProvider>
  </Provider>,
  document.getElementById('root'),
);
