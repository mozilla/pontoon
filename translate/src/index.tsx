import TimeAgo from 'javascript-time-ago';
import en from 'javascript-time-ago/locale/en.json';
import React from 'react';
import { render } from 'react-dom';
import { Provider } from 'react-redux';

import App from './App';
import { LocationProvider } from './context/location';
import { PluralFormProvider } from './context/pluralForm';
import { AppLocalizationProvider } from './core/l10n/components/AppLocalizationProvider';
import history from './historyInstance';
import './index.css';
import store from './store';

// TODO: Once we have support for more locales in Pontoon, we should
// make TimeAgo internationalized and initialize all locales here.
// See: https://www.npmjs.com/package/react-time-ago
TimeAgo.addLocale(en);

render(
  <Provider store={store}>
    <LocationProvider history={history}>
      <PluralFormProvider>
        <AppLocalizationProvider>
          <App />
        </AppLocalizationProvider>
      </PluralFormProvider>
    </LocationProvider>
  </Provider>,
  document.getElementById('root'),
);
