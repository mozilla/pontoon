/* @flow */

import { push, replace } from 'connected-react-router';

/**
 * Update the URL with a set of new parameters.
 *
 * This function removes the `string` parameter from the URL if any, because
 * it is possible that after the results have changed, the currently selected
 * entity won't be available anymore.
 * It keeps all other unaffected parameters in the URL the same.
 *
 * @param {Object} router The router data object from connected-react-router.
 * @param {Object} params A list of parameters to update in the current URL.
 * @param {boolean} replaceHistory Whether or not to push a new URL or replace the current one in the browser history.
 */
export function update(
    router: Object,
    params: { [string]: ?string },
    replaceHistory?: boolean,
): Function {
    return (dispatch) => {
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
            } else {
                currentParams.set(param, value);
            }
        });

        // If the URL did not change, don't do anything.
        if (queryString === '?' + currentParams.toString()) {
            return;
        }

        // When we change the URL, we want to remove the `string` parameter
        // because with the new results, that entity might not be available
        // anymore.
        if (!params['string']) {
            currentParams.delete('string');
        }

        let updateMethod = push;
        if (replaceHistory) {
            updateMethod = replace;
        }

        dispatch(updateMethod('?' + currentParams.toString()));
    };
}

/**
 * Update the URL with a new `author` parameter.
 *
 * This function removes the `string` parameter from the URL if any, because
 * it is possible that after the results have changed, the currently selected
 * entity won't be available anymore.
 * It keeps all other parameters in the URL the same.
 */
export function updateAuthor(router: Object, author: ?string): Function {
    return update(router, { author });
}

/**
 * Update the URL with a new `string` parameter.
 *
 * This function keeps all other parameters in the URL the same.
 */
export function updateEntity(
    router: Object,
    entity: string,
    replaceHistory?: boolean,
): Function {
    return update(router, { string: entity }, replaceHistory);
}

/**
 * Update the URL with a new `extra` parameter.
 *
 * This function removes the `string` parameter from the URL if any, because
 * it is possible that after the results have changed, the currently selected
 * entity won't be available anymore.
 * It keeps all other parameters in the URL the same.
 */
export function updateExtra(router: Object, extra: ?string): Function {
    return update(router, { extra });
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

/**
 * Update the URL with a new `tag` parameter.
 *
 * This function removes the `string` parameter from the URL if any, because
 * it is possible that after the results have changed, the currently selected
 * entity won't be available anymore.
 * It keeps all other parameters in the URL the same.
 */
export function updateTag(router: Object, tag: ?string): Function {
    return update(router, { tag });
}

/**
 * Update the URL with a new `time` parameter.
 *
 * This function removes the `string` parameter from the URL if any, because
 * it is possible that after the results have changed, the currently selected
 * entity won't be available anymore.
 * It keeps all other parameters in the URL the same.
 */
export function updateTime(router: Object, time: ?string): Function {
    return update(router, { time });
}

export default {
    update,
    updateAuthor,
    updateEntity,
    updateExtra,
    updateSearch,
    updateStatus,
    updateTag,
    updateTime,
};
