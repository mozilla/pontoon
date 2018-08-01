/* @flow */

import { combineReducers } from 'redux';

import * as entitieslist from 'modules/entitieslist';


// Combine reducers from all modules, using their
// NAME constant as key.
export default combineReducers({
    [entitieslist.NAME]: entitieslist.reducer,
});
