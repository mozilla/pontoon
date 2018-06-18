export const REQUEST = 'entitieslist/REQUEST';
export const RECEIVE = 'entitieslist/RECEIVE';


export function request(locale, project) {
    return {
        type: REQUEST,
    };
}

export function receive(entities) {
    return {
        type: RECEIVE,
        entities,
    };
}

export function get(locale, project, resource) {
    return dispatch => {
        dispatch(request(locale, project, resource));

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
        .then(response => response.json())
        .then(content => dispatch(receive(content.entities)));
    };
}
