/* @flow */


export const UPDATE: 'user/UPDATE' = 'user/UPDATE';


/**
 * Update the user data.
 */
export type UpdateAction = {
    +type: typeof UPDATE,
    +data: Object,
};
export function update(data: Object): UpdateAction {
    return {
        type: UPDATE,
        data,
    };
}


/**
 * Get data about the current user from the server.
 *
 * This will fetch data about whether the user is authenticated or not,
 * and if so, get their information and permissions.
 */
export function get(): Function {
    return async dispatch => {
        const url = new URL('/user-data/', window.location.origin);
        const response = await fetch(url);
        const content = await response.json();
        dispatch(update(content));
    }
}


export default {
    update,
};
