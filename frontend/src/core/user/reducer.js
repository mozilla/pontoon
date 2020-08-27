/* @flow */

import { RECEIVE_USERS, UPDATE, UPDATE_SETTINGS } from './actions';

import type { ReceiveAction, UpdateAction, UpdateSettingsAction } from './actions';
import type { UsersList } from 'core/api';


type Action =
    | ReceiveAction
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
            if (!action.data.settings) {
                return state;
            }
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


export type Notification = {|
    +id: number,
    +level: string,
    +unread: string,
    +description: {
        +content: string,
        +safe: boolean,
    },
    +verb: string,
    +date: string,
    +date_iso: string,
    +actor: {
        +anchor: string,
        +url: string,
    },
    +target: {
        +anchor: string,
        +url: string,
    },
|};


export type Notifications = {|
    has_unread: boolean,
    notifications: Array<Notification>,
|};


export type UserState = {|
    +isAuthenticated: boolean,
    +isAdmin: boolean,
    +id: string,
    +displayName: string,
    +nameOrEmail: string,
    +email: string,
    +username: string,
    +managerForLocales: Array<string>,
    +translatorForLocales: Array<string>,
    +translatorForProjects: { [string]: boolean },
    +settings: SettingsState,
    +tourStatus: ?number,
    +signInURL: string,
    +signOutURL: string,
    +gravatarURLSmall: string,
    +gravatarURLBig: string,
    +notifications: Notifications,
    +users: Array<UsersList>,
|};

const initial: UserState = {
    isAuthenticated: false,
    isAdmin: false,
    id: '',
    displayName: '',
    nameOrEmail: '',
    email: '',
    username: '',
    managerForLocales: [],
    translatorForLocales: [],
    translatorForProjects: {},
    settings: initialSettings,
    tourStatus: null,
    signInURL: '',
    signOutURL: '',
    gravatarURLSmall: '',
    gravatarURLBig: '',
    notifications: {
        has_unread: false,
        notifications: [],
    },
    users: [],
};

export default function reducer(
    state: UserState = initial,
    action: Action,
): UserState {
    switch (action.type) {
        case RECEIVE_USERS:
            return {
                ...state,
                users: action.users,
            };
        case UPDATE:
            return {
                ...state,
                isAuthenticated: action.data.is_authenticated,
                isAdmin: action.data.is_admin,
                id: action.data.id,
                displayName: action.data.display_name,
                nameOrEmail: action.data.name_or_email,
                email: action.data.email,
                username: action.data.username,
                managerForLocales: action.data.manager_for_locales,
                translatorForLocales: action.data.translator_for_locales,
                translatorForProjects: action.data.translator_for_projects,
                settings: settings(state.settings, action),
                tourStatus: action.data.tour_status,
                signInURL: action.data.login_url,
                signOutURL: action.data.logout_url,
                gravatarURLSmall: action.data.gravatar_url_small,
                gravatarURLBig: action.data.gravatar_url_big,
                notifications: action.data.notifications,
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
