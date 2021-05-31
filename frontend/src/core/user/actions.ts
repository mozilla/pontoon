import api from 'core/api';
import * as notification from 'core/notification';

import type { UsersList } from 'core/api';

export const RECEIVE_USERS: 'users/RECEIVE_USERS' = 'users/RECEIVE_USERS';
export const UPDATE: 'user/UPDATE' = 'user/UPDATE';
export const UPDATE_SETTINGS: 'user/UPDATE_SETTINGS' = 'user/UPDATE_SETTINGS';

export type ReceiveAction = {
    readonly type: typeof RECEIVE_USERS;
    readonly users: Array<UsersList>;
};
export function receive(users: Array<UsersList>): ReceiveAction {
    return {
        type: RECEIVE_USERS,
        users,
    };
}

/**
 * Update Interactive Tour status to a given step.
 */
export function updateTourStatus(step: number): (...args: Array<any>) => any {
    return async () => {
        await api.user.updateTourStatus(step);
    };
}

export type Settings = {
    runQualityChecks?: boolean;
    forceSuggestions?: boolean;
};

/**
 * Update the user settings.
 */
export type UpdateSettingsAction = {
    readonly type: typeof UPDATE_SETTINGS;
    readonly settings: Settings;
};
export function updateSettings(settings: Settings): UpdateSettingsAction {
    return {
        type: UPDATE_SETTINGS,
        settings,
    };
}

/**
 * Update the user data.
 */
export type UpdateAction = {
    readonly type: typeof UPDATE;
    readonly data: Record<string, any>;
};
export function update(data: Record<string, any>): UpdateAction {
    return {
        type: UPDATE,
        data,
    };
}

/**
 * Sign out the current user.
 */
export function signOut(url: string): (...args: Array<any>) => any {
    return async (dispatch) => {
        await api.user.signOut(url);

        dispatch(get());
    };
}

function _getOperationNotif(setting, value) {
    if (setting === 'runQualityChecks' && value) {
        return notification.messages.CHECKS_ENABLED;
    }
    if (setting === 'runQualityChecks' && !value) {
        return notification.messages.CHECKS_DISABLED;
    }
    if (setting === 'forceSuggestions' && value) {
        return notification.messages.SUGGESTIONS_ENABLED;
    }
    if (setting === 'forceSuggestions' && !value) {
        return notification.messages.SUGGESTIONS_DISABLED;
    }

    throw new Error('Unsupported operation on setting: ' + setting);
}

export function saveSetting(
    setting: string,
    value: boolean,
    username: string,
): (...args: Array<any>) => any {
    return async (dispatch) => {
        dispatch(updateSettings({ [setting]: value }));

        await api.user.updateSetting(username, setting, value);

        const notif = _getOperationNotif(setting, value);
        dispatch(notification.actions.add(notif));
    };
}

export function markAllNotificationsAsRead(): (...args: Array<any>) => any {
    return async (dispatch) => {
        await api.user.markAllNotificationsAsRead();

        dispatch(get());
    };
}

export function getUsers(): (...args: Array<any>) => any {
    return async (dispatch) => {
        const content = await api.user.getUsers();
        dispatch(receive(content));
    };
}

/**
 * Get data about the current user from the server.
 *
 * This will fetch data about whether the user is authenticated or not,
 * and if so, get their information and permissions.
 */
export function get(): (...args: Array<any>) => any {
    return async (dispatch) => {
        const content = await api.user.get();
        dispatch(update(content));
    };
}

export function dismissAddonPromotion(): (...args: Array<any>) => any {
    return async (dispatch) => {
        await api.user.dismissAddonPromotion();

        dispatch(get());
    };
}

export default {
    dismissAddonPromotion,
    get,
    getUsers,
    markAllNotificationsAsRead,
    saveSetting,
    signOut,
    update,
    updateSettings,
    updateTourStatus,
};
