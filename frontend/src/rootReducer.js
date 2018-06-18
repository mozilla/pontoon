import { combineReducers } from 'redux';

import navigation from 'core/navigation';
import entitieslist from 'modules/entitieslist';


const rootReducer = combineReducers({
    [entitieslist.constants.NAME]: entitieslist.reducer,
    [navigation.constants.NAME]: navigation.reducer,
});

export default rootReducer;
