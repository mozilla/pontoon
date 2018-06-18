import { RECEIVE } from './actions';


const initial = {
    entities: [],
    fetching: false,
    errors: [],
};

export default function reducer(state = initial, action) {
    switch (action.type) {
        case RECEIVE:
            return Object.assign({}, state, {entities: action.entities});
        default:
            return state;
    }
}
