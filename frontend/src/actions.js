function requestEntitiesList(locale, project) {
    return {
        type: 'FETCHING_ENTITIES_LIST',
    };
}

function receiveEntitiesList(entities) {
    return {
        type: 'RECEIVED_ENTITIES_LIST',
        entities,
    };
}

export function fetchEntitiesList(locale, project) {
    return dispatch => {
        dispatch(requestEntitiesList(locale, project));
        // Fetch entities from backend.
        const url = new URL('http://localhost:8000/get-entities/');
        const payload = new FormData();
        payload.append('locale', locale);
        payload.append('project', project);

        const requestParams = {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: payload,
        };

        fetch(url, requestParams)
        .then(response => response.json())
        .then(content => dispatch(receiveEntitiesList(content.entities)));
    };
}
