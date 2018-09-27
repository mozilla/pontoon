/* @flow */

import { combineReducers } from 'redux';

import * as lightbox from 'core/lightbox';
import * as locales from 'core/locales';
import * as plural from 'core/plural';
import * as user from 'core/user';
import * as entitieslist from 'modules/entitieslist';
import * as history from 'modules/history';


// Combine reducers from all modules, using their NAME constant as key.
export default combineReducers({
    [lightbox.NAME]: lightbox.reducer,
    [locales.NAME]: locales.reducer,
    [plural.NAME]: plural.reducer,
    [user.NAME]: user.reducer,
    [entitieslist.NAME]: entitieslist.reducer,
    [history.NAME]: history.reducer,
});
