/* @flow */

import { combineReducers } from 'redux';

import navigation from 'core/navigation';
import entitieslist from 'modules/entitieslist';


// Combine reducers from all modules, using their
// NAME constant as key.
const rootReducer = combineReducers({
    [entitieslist.constants.NAME]: entitieslist.reducer,
    [navigation.constants.NAME]: navigation.reducer,
});

export default rootReducer;
