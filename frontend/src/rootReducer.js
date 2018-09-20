/* @flow */

import { combineReducers } from 'redux';

import * as lightbox from 'core/lightbox';
import * as entitieslist from 'modules/entitieslist';
import * as history from 'modules/history';


// Combine reducers from all modules, using their
// NAME constant as key.
export default combineReducers({
    [lightbox.NAME]: lightbox.reducer,
    [entitieslist.NAME]: entitieslist.reducer,
    [history.NAME]: history.reducer,
});
