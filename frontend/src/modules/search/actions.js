/* @flow */

import { push } from 'connected-react-router';

export const UPDATE: 'search/UPDATE' = 'search/UPDATE';


/**
 * Update the current search content.
 */
export function updateSearch(search: ?string, router: Object): Function {
    return dispatch => {
        const queryString = router.location.search;
        const params = new URLSearchParams(queryString);
        const prevSearch = params.get('search');

        if (search === prevSearch || (!search && !prevSearch)) {
            return;
        }

        if (!search) {
            params.delete('search');
        }
        else {
            params.set('search', search);
        }

        dispatch(push('?' + params.toString()));
    };
}

export function updateStatus(status: ?string, router: Object): Function {
    return dispatch => {
        const queryString = router.location.search;
        const params = new URLSearchParams(queryString);
        const prevStatus = params.get('status');

        if (status === prevStatus || (!status && !prevStatus)) {
            return;
        }

        if (!status) {
            params.delete('status');
        }
        else {
            params.set('status', status);
        }

        dispatch(push('?' + params.toString()));
    };
}


export default {
    updateSearch,
    updateStatus,
};
