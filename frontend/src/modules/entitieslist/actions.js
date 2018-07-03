/* @flow */

export const REQUEST: 'entitieslist/REQUEST' = 'entitieslist/REQUEST';
export const RECEIVE: 'entitieslist/RECEIVE' = 'entitieslist/RECEIVE';


export type RequestAction = {
    type: typeof REQUEST,
};
export function request(): RequestAction {
    return {
        type: REQUEST,
    };
}


export type ReceiveAction = {
    type: typeof RECEIVE,
    entities: Array<Object>,
};
export function receive(entities: Array<Object>): ReceiveAction {
    return {
        type: RECEIVE,
        entities,
    };
}


export function get(
    locale: string,
    project: string,
    resource: string,
): Function {
    return (dispatch: Function): void => {
        dispatch(request());

        // Fetch entities from backend.
        const url = new URL('http://localhost:8000/get-entities/');
        const payload = new FormData();
        payload.append('locale', locale);
        payload.append('project', project);
        payload.append('paths[]', resource);

        const requestParams = {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: payload,
        };

        fetch(url, requestParams)
        .then((response: Object) => response.json())
        .then((content: Object) => dispatch(receive(content.entities)));
    };
}
