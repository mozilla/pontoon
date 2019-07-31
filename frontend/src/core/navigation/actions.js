/* @flow */

import { push } from 'connected-react-router';


/**
 * Update the URL with a set of new parameters.
 *
 * This function removes the `string` parameter from the URL if any, because
 * it is possible that after the results have changed, the currently selected
 * entity won't be available anymore.
 * It keeps all other unaffected parameters in the URL the same.
 */
export function update(router: Object, params: { [string]: ?string }): Function {
    return dispatch => {
        const queryString = router.location.search;
        const currentParams = new URLSearchParams(queryString);

        Object.keys(params).forEach((param: string) => {
            const prev = currentParams.get(param);
            const value = params[param];

            if (value === prev || (!value && !prev)) {
                return;
            }

            if (!value) {
                currentParams.delete(param);
            }
            else {
                currentParams.set(param, value);
            }
        });

        // When we change the URL, we want to remove the `string` parameter
        // because with the new results, that entity might not be available
        // anymore.
        if (!params['string']) {
            currentParams.delete('string');
        }

        dispatch(push('?' + currentParams.toString()));
    }
}


/**
 * Update the URL with a new `string` parameter.
 *
 * This function keeps all other parameters in the URL the same.
 */
export function updateEntity(router: Object, entity: string): Function {
    return update(router, { string: entity });
}


/**
 * Update the URL with a new `search` parameter.
 *
 * This function removes the `string` parameter from the URL if any, because
 * it is possible that after the results have changed, the currently selected
 * entity won't be available anymore.
 * It keeps all other parameters in the URL the same.
 */
export function updateSearch(router: Object, search: ?string): Function {
    return update(router, { search });
}


/**
 * Update the URL with a new `status` parameter.
 *
 * This function removes the `string` parameter from the URL if any, because
 * it is possible that after the results have changed, the currently selected
 * entity won't be available anymore.
 * It keeps all other parameters in the URL the same.
 */
export function updateStatus(router: Object, status: ?string): Function {
    return update(router, { status });
}


export default {
    update,
    updateEntity,
    updateSearch,
    updateStatus,
};
