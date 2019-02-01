/* @flow */

import { combineReducers } from 'redux';

import * as lightbox from 'core/lightbox';
import * as locales from 'core/locales';
import * as l10n from 'core/l10n';
import * as plural from 'core/plural';
import * as stats from 'core/stats';
import * as user from 'core/user';
import * as entitieslist from 'modules/entitieslist';
import * as history from 'modules/history';
import * as machinery from 'modules/machinery';
import * as otherlocales from 'modules/otherlocales';


// Combine reducers from all modules, using their NAME constant as key.
export default combineReducers({
    // Core modules
    [lightbox.NAME]: lightbox.reducer,
    [locales.NAME]: locales.reducer,
    [l10n.NAME]: l10n.reducer,
    [plural.NAME]: plural.reducer,
    [stats.NAME]: stats.reducer,
    [user.NAME]: user.reducer,
    // Application modules
    [entitieslist.NAME]: entitieslist.reducer,
    [history.NAME]: history.reducer,
    [machinery.NAME]: machinery.reducer,
    [otherlocales.NAME]: otherlocales.reducer,
});
