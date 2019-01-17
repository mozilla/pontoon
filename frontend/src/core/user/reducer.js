/* @flow */

import { UPDATE, UPDATE_SETTINGS } from './actions';

import type { UpdateAction, UpdateSettingsAction } from './actions';


type Action =
    | UpdateAction
    | UpdateSettingsAction
;


export type SettingsState = {|
    +runQualityChecks: boolean,
    +forceSuggestions: boolean,
|};

const initialSettings: SettingsState = {
    runQualityChecks: true,
    forceSuggestions: true,
};

function settings(
    state: SettingsState = initialSettings,
    action: Action,
): SettingsState {
    switch (action.type) {
        case UPDATE:
            return {
                runQualityChecks: action.data.settings.quality_checks,
                forceSuggestions: action.data.settings.force_suggestions,
            };
        case UPDATE_SETTINGS:
            return {
                ...state,
                ...action.settings,
            };
        default:
            return state;
    }
}


export type UserState = {|
    +isAuthenticated: boolean,
    +id: string,
    +displayName: string,
    +email: string,
    +username: string,
    +managerForLocales: Array<string>,
    +translatorForLocales: Array<string>,
    +translatorForProjects: Array<string>,
    +settings: SettingsState,
|};

const initial: UserState = {
    isAuthenticated: false,
    id: '',
    displayName: '',
    email: '',
    username: '',
    managerForLocales: [],
    translatorForLocales: [],
    translatorForProjects: [],
    settings: initialSettings,
};

export default function reducer(
    state: UserState = initial,
    action: Action,
): UserState {
    switch (action.type) {
        case UPDATE:
            let newSettings = { ...state.settings };

            // We only want to update the settings from the server once, because
            // otherwise we risk erasing local changes to those settings.
            // Thus, we check if the previous state of isAuthenticated is
            // false, which indicates either that this is the first update
            // or that the user was logged out, in which case the values
            // should be overwritten.
            if (!state.isAuthenticated && action.data.is_authenticated) {
                newSettings = settings(state.settings, action)
            }

            return {
                isAuthenticated: action.data.is_authenticated,
                id: action.data.id,
                displayName: action.data.display_name,
                email: action.data.email,
                username: action.data.username,
                managerForLocales: action.data.manager_for_locales,
                translatorForLocales: action.data.translator_for_locales,
                translatorForProjects: action.data.translator_for_projects,
                settings: newSettings,
            };
        case UPDATE_SETTINGS:
            return {
                ...state,
                settings: settings(state.settings, action),
            };
        default:
            return state;
    }
}
