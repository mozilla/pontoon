/* @flow */

export const RECEIVE: 'RECEIVE' = 'RECEIVE';
export const REQUEST: 'REQUEST' = 'REQUEST';
export const ERROR: 'ERROR' = 'ERROR';

type Action = {|
    +type: String,
    +payload: any,
|};


export type State = {|
    +requests: Array<String>,
    +receives: Array<String>,
    +errors: Array<String>
|};

const initialState = {
    requests: [],
    receives: [],
    errors: [],
};

export default function reducer(
    state: State = initialState,
    action: Action,
): State {
    const fetchAction = action.type.match(/([a-zA-Z]+)\/(REQUEST|RECEIVE|ERROR)/)

    if (!fetchAction) {
        return state;
    }
    const component: String = fetchAction[1];
    const fetchPhase: fetchAction = fetchAction[2];

    switch (fetchPhase) {
        case REQUEST:
            return {
                ...state,
                requests: state.requests.concat(component)
            };
        case RECEIVE:
            return {
                ...state,
                receives: state.receives.concat(component)
            };
        case ERROR:
            return {
                ...state,
                errors: state.errors.concat(component)
            };
        default:
            return state
    }
}
