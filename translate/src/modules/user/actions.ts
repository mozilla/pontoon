import {
  dismissAddonPromotion,
  fetchUserData,
  markAllNotificationsAsRead,
  updateUserSetting,
  updateUserTheme,
} from '../../api/user';
import { NotificationMessage } from '../../context/Notification';
import {
  CHECKS_DISABLED,
  CHECKS_ENABLED,
  SUGGESTIONS_DISABLED,
  SUGGESTIONS_ENABLED,
} from '../../modules/notification/messages';
import type { AppThunk } from '../../store';

export const UPDATE = 'user/UPDATE';
export const UPDATE_SETTINGS = 'user/UPDATE_SETTINGS';
export const UPDATE_THEME = 'user/UPDATE_THEME';

export type Action = UpdateAction | UpdateSettingsAction | UpdateThemeAction;

/**
 * Update the user data.
 */
export type UpdateAction = {
  readonly type: typeof UPDATE;
  readonly data: Record<string, any>;
};

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

/**
 * Update the user theme.
 */
export type UpdateThemeAction = {
  readonly type: typeof UPDATE_THEME;
  readonly theme: string;
};

function getNotification(setting: keyof Settings, value: boolean) {
  switch (setting) {
    case 'runQualityChecks':
      return value ? CHECKS_ENABLED : CHECKS_DISABLED;
    case 'forceSuggestions':
      return value ? SUGGESTIONS_ENABLED : SUGGESTIONS_DISABLED;
    default:
      throw new Error('Unsupported operation on setting: ' + setting);
  }
}

export function saveSetting(
  setting: keyof Settings,
  value: boolean,
  username: string,
  showNotification: (message: NotificationMessage) => void,
): AppThunk {
  return async (dispatch) => {
    dispatch({ type: UPDATE_SETTINGS, settings: { [setting]: value } });
    await updateUserSetting(username, setting, value);

    const notif = getNotification(setting, value);
    showNotification(notif);
  };
}

export function saveTheme(theme: string, username: string): AppThunk {
  return async (dispatch) => {
    await updateUserTheme(username, theme);

    dispatch({ type: UPDATE_THEME, theme });
  };
}

export const markAllNotificationsAsRead_ = (): AppThunk => async (dispatch) => {
  await markAllNotificationsAsRead();
  dispatch(getUserData());
};

/**
 * Get data about the current user from the server.
 *
 * This will fetch data about whether the user is authenticated or not,
 * and if so, get their information and permissions.
 */
export const getUserData = (): AppThunk => async (dispatch) => {
  dispatch({ type: UPDATE, data: await fetchUserData() });
};

export const dismissAddonPromotion_ = (): AppThunk => async (dispatch) => {
  await dismissAddonPromotion();
  dispatch(getUserData());
};
