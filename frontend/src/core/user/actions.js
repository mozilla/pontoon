/* @flow */

import api from 'core/api';

export const UPDATE: 'user/UPDATE' = 'user/UPDATE';
export const UPDATE_SETTINGS: 'user/UPDATE_SETTINGS' = 'user/UPDATE_SETTINGS';


export type Settings = {
    runQualityChecks: boolean,
    forceSuggestions: boolean,
};


/**
 * Update the user data.
 */
export type UpdateAction = {|
    +type: typeof UPDATE,
    +data: Object,
|};
export function update(data: Object): UpdateAction {
    return {
        type: UPDATE,
        data,
    };
}


/**
 * Update the user settings.
 */
export type UpdateSettingsAction = {|
    +type: typeof UPDATE_SETTINGS,
    +settings: Settings,
|};
export function updateSettings(settings: Settings): UpdateSettingsAction {
    return {
        type: UPDATE_SETTINGS,
        settings,
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
        const content = await api.user.get();
        dispatch(update(content));
    }
}


export default {
    get,
    update,
    updateSettings,
};
