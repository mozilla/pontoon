/* @flow */

import { combineReducers } from 'redux';

import * as lightbox from 'core/lightbox';
import * as user from 'core/user';
import * as entitieslist from 'modules/entitieslist';
import * as history from 'modules/history';
import * as loader from 'modules/loader';


// Combine reducers from all modules, using their
// NAME constant as key.
export default combineReducers({
    [lightbox.NAME]: lightbox.reducer,
    [user.NAME]: user.reducer,
    [entitieslist.NAME]: entitieslist.reducer,
    [history.NAME]: history.reducer,
    [loader.NAME]: loader.reducer,
});
