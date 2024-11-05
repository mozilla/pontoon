import { Action, UPDATE, UPDATE_SETTINGS, UPDATE_THEME } from './actions';

// Name of this module.
// Used as the key to store this module's reducer.
export const USER = 'user';

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
  readonly isAuthenticated: boolean | null; // null while loading
  readonly isAdmin: boolean;
  readonly isPM: boolean;
  readonly id: string;
  readonly displayName: string;
  readonly nameOrEmail: string;
  readonly email: string;
  readonly username: string;
  readonly dateJoined: string;
  readonly contributorForLocales: Array<string>;
  readonly managerForLocales: Array<string>;
  readonly pmForProjects: Array<string>;
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
  readonly theme: string;
};

const initial: UserState = {
  isAuthenticated: null,
  isAdmin: false,
  isPM: false,
  id: '',
  displayName: '',
  nameOrEmail: '',
  email: '',
  username: '',
  dateJoined: '',
  contributorForLocales: [],
  managerForLocales: [],
  pmForProjects: [],
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
  theme: 'dark',
};

export function reducer(state: UserState = initial, action: Action): UserState {
  switch (action.type) {
    case UPDATE:
      return {
        isAuthenticated: action.data.is_authenticated ?? null,
        isAdmin: action.data.is_admin ?? false,
        isPM: action.data.is_pm ?? false,
        id: action.data.id ?? '',
        displayName: action.data.display_name ?? '',
        nameOrEmail: action.data.name_or_email ?? '',
        email: action.data.email ?? '',
        username: action.data.username ?? '',
        dateJoined: action.data.date_joined ?? '',
        contributorForLocales: action.data.contributor_for_locales ?? [],
        managerForLocales: action.data.manager_for_locales ?? [],
        pmForProjects: action.data.pm_for_projects ?? [],
        translatorForLocales: action.data.translator_for_locales ?? [],
        translatorForProjects: action.data.translator_for_projects ?? {},
        settings: settings(state.settings, action),
        tourStatus: action.data.tour_status ?? null,
        hasDismissedAddonPromotion:
          action.data.has_dismissed_addon_promotion ?? false,
        signInURL: action.data.login_url ?? '',
        signOutURL: action.data.logout_url ?? '',
        gravatarURLSmall: action.data.gravatar_url_small ?? '',
        gravatarURLBig: action.data.gravatar_url_big ?? '',
        notifications: action.data.notifications ?? {
          has_unread: false,
          notifications: [],
          unread_count: '0',
        },
        theme: action.data.theme ?? 'dark',
      };
    case UPDATE_SETTINGS:
      return {
        ...state,
        settings: settings(state.settings, action),
      };
    case UPDATE_THEME:
      return {
        ...state,
        theme: action.theme,
      };
    default:
      return state;
  }
}
