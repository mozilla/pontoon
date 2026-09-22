import { getCSRFToken } from './utils/csrfToken';

import type { BadgeInfo } from './translation';

export type UploadTranslationsResult = {
  readonly updated: number;
  readonly unchanged: number;
  readonly undefined_keys_count: number;
  readonly badge_updates?: BadgeInfo[];
};

export type UploadTranslationsResponse = {
  readonly status: number;
  readonly result?: UploadTranslationsResult;
  readonly error?: string;
};

/** First error message of a DRF error response, which is keyed by field name. */
function errorMessage(data: unknown): string | undefined {
  if (!data || typeof data !== 'object') {
    return undefined;
  }
  for (const value of Object.values(data)) {
    if (typeof value === 'string') {
      return value;
    }
    if (Array.isArray(value) && typeof value[0] === 'string') {
      return value[0];
    }
  }
  return undefined;
}

/** Upload a translation file, storing its translations as approved. */
export async function uploadTranslations(
  locale: string,
  project: string,
  resource: string,
  file: File,
): Promise<UploadTranslationsResponse> {
  const payload = new FormData();
  payload.append('locale', locale);
  payload.append('project', project);
  payload.append('resource', resource);
  payload.append('uploadfile', file);

  let response: Response;
  try {
    response = await fetch('/api/v2/upload/translations/', {
      method: 'POST',
      credentials: 'same-origin',
      headers: { 'X-CSRFToken': getCSRFToken() },
      body: payload,
    });
  } catch {
    // A network failure has no status of its own.
    return { status: 0 };
  }

  let data: unknown;
  try {
    data = await response.json();
  } catch {
    data = null;
  }

  return response.ok
    ? { status: response.status, result: data as UploadTranslationsResult }
    : { status: response.status, error: errorMessage(data) };
}
