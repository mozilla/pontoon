import { POST } from './utils/base';
import { getCSRFToken } from './utils/csrfToken';
import type { MessageEntry } from '~/utils/message';
import type { TranslationComment } from './comment';
import type { SourceType } from './machinery';
import { Message } from '@mozilla/l10n';

export type ChangeOperation = 'approve' | 'unapprove' | 'reject' | 'unreject';

export type ApiFailedChecks = {
  readonly clErrors?: string[];
  readonly pErrors?: string[];
  readonly clWarnings?: string[];
  readonly pndbWarnings?: string[];
  readonly ttWarnings?: string[];
};

/**
 * Accepted Translation of an Entity, cannot exist outside of the Entity type.
 */
export interface EntityTranslation {
  readonly pk: number;
  readonly status:
    | 'approved'
    | 'fuzzy'
    | 'pretranslated'
    | 'rejected'
    | 'unreviewed';
  readonly string: string | null | undefined;
  readonly value: Message;
  readonly properties?: Record<string, Message>;
  readonly errors?: string[];
  readonly warnings?: string[];
}

export interface HistoryTranslation extends EntityTranslation {
  readonly string: string;
  readonly date: string;
  readonly uid: number | null | undefined;
  readonly user: string;
  readonly username: string;
  readonly userGravatarUrlSmall: string;
  readonly userBanner?: [string, string];
  readonly approvedUser?: string;
  readonly approvedDate?: string;
  readonly rejectedDate?: string;
  readonly rejectedUser?: string;
  readonly machinerySources?: string;
  readonly comments?: TranslationComment[];
}

export type APIStats = {
  approved: number;
  pretranslated: number;
  warnings: number;
  errors: number;
  unreviewed: number;
  total: number;
};

export type BadgeInfo = {
  name: string;
  level: number;
};

type CreateTranslationResponse =
  | { status: false; same: true; failedChecks?: never }
  | { status: false; failedChecks: ApiFailedChecks; same?: never }
  | {
      status: true;
      translation: EntityTranslation;
      badge_update?: BadgeInfo;
      stats: APIStats;
    };

/**
 * Create a new translation.
 *
 * If a similar translation already exists, update it with the new data.
 * Otherwise, create it.
 */
export function createTranslation(
  entityId: number,
  entry: MessageEntry,
  localeCode: string,
  forceSuggestions: boolean,
  allResources: boolean,
  ignoreWarnings: boolean,
  machinerySources: SourceType[],
): Promise<CreateTranslationResponse> {
  const payload = new URLSearchParams({
    entity: String(entityId),
    value: JSON.stringify(entry.value ?? []),
    locale: localeCode,
    force_suggestions: String(forceSuggestions),
    machinery_sources: String(machinerySources),
    stats: allResources ? 'all' : 'resource',
  });

  if (entry.attributes?.size) {
    const attrObj = Object.fromEntries(entry.attributes);
    payload.append('properties', JSON.stringify(attrObj));
  }
  if (ignoreWarnings) {
    payload.append('ignore_warnings', ignoreWarnings.toString());
  }

  const csrfToken = getCSRFToken();
  payload.append('csrfmiddlewaretoken', csrfToken);

  const headers = new Headers({
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-CSRFToken': csrfToken,
  });

  return POST('/translations/create/', payload, { headers });
}

type SetTranslationStatusResponse =
  | {
      failedChecks: ApiFailedChecks;
      status?: never;
      string: string;
    } // indicates failed approve
  | {
      status: true;
      translation: EntityTranslation | null;
      stats: APIStats;
      badge_update?: BadgeInfo;
      failedChecks?: never;
    };

export function setTranslationStatus(
  change: ChangeOperation,
  id: number,
  resource: string,
  ignoreWarnings: boolean,
): Promise<SetTranslationStatusResponse> {
  const url = `/translations/${change}/`;

  const payload = new URLSearchParams({
    translation: String(id),
    stats: resource == 'all-resources' ? 'all' : 'resource',
  });
  if (change === 'approve' && ignoreWarnings) {
    payload.append('ignore_warnings', 'true');
  }

  const headers = new Headers({ 'X-CSRFToken': getCSRFToken() });

  return POST(url, payload, { headers });
}

export function deleteTranslation(id: number): Promise<{ status: true }> {
  const payload = new URLSearchParams({ translation: String(id) });
  const headers = new Headers({ 'X-CSRFToken': getCSRFToken() });
  return POST('/translations/delete/', payload, { headers });
}
