import { combineReducers } from 'redux';


const initialParams = {
    locale: 'af',
    project: 'amo',
    entity: null,
};
function parameters(state = initialParams, action) {
    switch (action.type) {
        default:
            return state;
    }
}

function entities(state = [], action) {
    switch (action.type) {
        case 'RECEIVED_ENTITIES_LIST':
            return action.entities;
        default:
            return state;
    }
}


const rootReducer = combineReducers({
    parameters,
    entities,
});

export default rootReducer;
