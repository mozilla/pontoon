import { RECEIVE_USERS, UPDATE, UPDATE_SETTINGS } from './actions';

import type {
    ReceiveAction,
    UpdateAction,
    UpdateSettingsAction,
} from './actions';
import type { UsersList } from 'core/api';

type Action = ReceiveAction | UpdateAction | UpdateSettingsAction;

export type SettingsState = {
    readonly runQualityChecks: boolean;
    readonly forceSuggestions: boolean;
};

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

export type Notification = {
    readonly id: number;
    readonly level: string;
    readonly unread: string;
    readonly description: {
        readonly content: string;
        readonly is_comment: boolean;
    };
    readonly verb: string;
    readonly date: string;
    readonly date_iso: string;
    readonly actor: {
        readonly anchor: string;
        readonly url: string;
    };
    readonly target: {
        readonly anchor: string;
        readonly url: string;
    };
};

export type Notifications = {
    has_unread: boolean;
    notifications: Array<Notification>;
    unread_count: string;
};

export type UserState = {
    readonly isAuthenticated: boolean;
    readonly isAdmin: boolean;
    readonly id: string;
    readonly displayName: string;
    readonly nameOrEmail: string;
    readonly email: string;
    readonly username: string;
    readonly managerForLocales: Array<string>;
    readonly translatorForLocales: Array<string>;
    readonly translatorForProjects: Record<string, boolean>;
    readonly settings: SettingsState;
    readonly tourStatus: number | null | undefined;
    readonly hasDismissedAddonPromotion: boolean;
    readonly signInURL: string;
    readonly signOutURL: string;
    readonly gravatarURLSmall: string;
    readonly gravatarURLBig: string;
    readonly notifications: Notifications;
    readonly users: Array<UsersList>;
};

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
    hasDismissedAddonPromotion: false,
    signInURL: '',
    signOutURL: '',
    gravatarURLSmall: '',
    gravatarURLBig: '',
    notifications: {
        has_unread: false,
        notifications: [],
        unread_count: '0',
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
                hasDismissedAddonPromotion:
                    action.data.has_dismissed_addon_promotion,
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
