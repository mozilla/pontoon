import { GET, POST } from './utils/base';
import { getCSRFToken } from './utils/csrfToken';

export type Notification = {
  id: number;
  level: string;
  unread: string;
  description: {
    content: string;
    is_comment: boolean;
  };
  verb: string;
  date: string;
  date_iso: string;
  actor: {
    anchor: string;
    url: string;
  };
  target: {
    anchor: string;
    url: string;
  };
};

export type ApiUserData = {
  is_authenticated?: boolean;
  is_admin?: boolean;
  id?: string;
  display_name?: string;
  name_or_email?: string;
  email?: string;
  username?: string;
  manager_for_locales?: string[];
  translator_for_locales?: string[];
  translator_for_projects?: Record<string, boolean>;
  settings?: { quality_checks: boolean; force_suggestions: boolean };
  tour_status?: number;
  has_dismissed_addon_promotion?: boolean;
  login_url?: string;
  logout_url?: string;
  gravatar_url_small?: string;
  gravatar_url_big?: string;
  notifications?: {
    has_unread: boolean;
    notifications: Notification[];
    unread_count: string;
  };
};

/** All users for use in mentions suggestions within comments */
export type MentionUser = {
  gravatar: string;
  name: string;
  url: string;
};

/** Dismiss Add-On Promotion. */
export const dismissAddonPromotion = (): Promise<void> =>
  GET('/dismiss-addon-promotion/');

/** Return data about the current user from the server. */
export const fetchUserData = (): Promise<ApiUserData> => GET('/user-data/');

/** Get all users from server. */
export const fetchUsersList = (): Promise<MentionUser[]> => GET('/get-users/');

/** Mark all notifications of the current user as read. */
export const markAllNotificationsAsRead = (): Promise<void> =>
  GET('/notifications/mark-all-as-read/');

export function updateUserSetting(
  username: string,
  setting: 'forceSuggestions' | 'runQualityChecks',
  value: boolean,
): Promise<string> {
  let attribute: string;
  switch (setting) {
    case 'forceSuggestions':
      attribute = 'force_suggestions';
      break;
    case 'runQualityChecks':
      attribute = 'quality_checks';
      break;
  }

  const csrfToken = getCSRFToken();
  const payload = new URLSearchParams({
    attribute,
    value: String(value),
    csrfmiddlewaretoken: csrfToken,
  });
  const headers = new Headers({ 'X-CSRFToken': csrfToken });
  return POST(`/api/v1/user/${username}/`, payload, { headers });
}

/** Update Interactive Tour status to a given step. */
export function updateTourStatus(step: number): Promise<void> {
  const csrfToken = getCSRFToken();
  const payload = new URLSearchParams({
    tour_status: String(step),
    csrfmiddlewaretoken: csrfToken,
  });
  const headers = new Headers({ 'X-CSRFToken': csrfToken });
  return POST('/update-tour-status/', payload, { headers });
}
