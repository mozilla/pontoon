import { POST } from './utils/base';
import { getCSRFToken } from './utils/csrfToken';
import type { TranslationComment } from './comment';
import type { SourceType } from './machinery';

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
export type EntityTranslation = {
  readonly pk: number;
  readonly string: string | null | undefined;
  readonly approved: boolean;
  readonly pretranslated: boolean;
  readonly fuzzy: boolean;
  readonly rejected: boolean;
  readonly errors: string[];
  readonly warnings: string[];
};

export type HistoryTranslation = {
  readonly approved: boolean;
  readonly approvedUser: string;
  readonly pretranslated: boolean;
  readonly date: string;
  readonly dateIso: string;
  readonly fuzzy: boolean;
  readonly pk: number;
  readonly rejected: boolean;
  readonly string: string;
  readonly uid: number | null | undefined;
  readonly rejectedUser: string;
  readonly machinerySources: string;
  readonly user: string;
  readonly username: string;
  readonly userGravatarUrlSmall: string;
  readonly comments: Array<TranslationComment>;
};

export type APIStats = {
  approved: number;
  pretranslated: number;
  warnings: number;
  errors: number;
  unreviewed: number;
  total: number;
};

type CreateTranslationResponse =
  | { status: false; same: true; failedChecks?: never }
  | { status: false; failedChecks: ApiFailedChecks; same?: never }
  | { status: true; translation: EntityTranslation; stats: APIStats };

/**
 * Create a new translation.
 *
 * If a similar translation already exists, update it with the new data.
 * Otherwise, create it.
 */
export function createTranslation(
  entityId: number,
  translation: string,
  localeCode: string,
  pluralForm: number,
  original: string,
  forceSuggestions: boolean,
  resource: string,
  ignoreWarnings: boolean,
  machinerySources: SourceType[],
): Promise<CreateTranslationResponse> {
  const payload = new URLSearchParams({
    entity: String(entityId),
    translation,
    locale: localeCode,
    plural_form: String(pluralForm),
    original,
    force_suggestions: String(forceSuggestions),
    machinery_sources: String(machinerySources),
  });

  if (resource !== 'all-resources') {
    payload.append('paths[]', resource);
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

type SetTranslationResponse =
  | { failedChecks: ApiFailedChecks; string: string } // indicates failed approve
  | { translation: EntityTranslation; stats: APIStats; failedChecks?: never };

export function setTranslationStatus(
  change: ChangeOperation,
  id: number,
  resource: string,
  ignoreWarnings: boolean,
): Promise<SetTranslationResponse> {
  const url = `/translations/${change}/`;

  const payload = new URLSearchParams({ translation: String(id) });
  if (resource !== 'all-resources') {
    payload.append('paths[]', resource);
  }
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
