/* @flow */

import { push } from 'connected-react-router';

export const UPDATE: 'search/UPDATE' = 'search/UPDATE';


/**
 * Update the current search content.
 */
export function update(search: ?string, router: Object): Function {
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
    }
}


export default {
    update,
};
