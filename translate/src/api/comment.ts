import type { HistoryTranslation } from './translation';
import { GET, POST } from './utils/base';
import { getCSRFToken } from './utils/csrfToken';
import { keysToCamelCase } from './utils/keysToCamelCase';

/**
 * Comments pertaining to a translation.
 */
export type TranslationComment = {
  readonly author: string;
  readonly username: string;
  readonly userBanner: string[];
  readonly userGravatarUrlSmall: string;
  readonly createdAt: string;
  readonly dateIso: string;
  readonly content: string;
  readonly pinned: boolean;
  readonly id: number;
};

/**
 * Alias to be used for comments pertaining to a Locale
 */
export type TeamComment = TranslationComment;

export async function fetchTeamComments(
  entity: number,
  locale: string,
): Promise<TeamComment[]> {
  const search = new URLSearchParams({ entity: String(entity), locale });
  const results = await GET('/get-team-comments/', search, { singleton: true });
  return Array.isArray(results) ? keysToCamelCase(results) : [];
}

export function addComment(
  entity: number,
  locale: string,
  comment: string,
  translation: HistoryTranslation | null,
): Promise<void> {
  const payload = new URLSearchParams({
    entity: String(entity),
    locale,
    comment,
  });
  if (translation) {
    payload.append('translation', String(translation.pk));
  }
  const headers = new Headers({ 'X-CSRFToken': getCSRFToken() });
  return POST('/add-comment/', payload, { headers });
}

export function setCommentPinned(
  commentId: number,
  pinned: boolean,
): Promise<void> {
  const url = pinned ? '/pin-comment/' : '/unpin-comment/';
  const payload = new URLSearchParams({ comment_id: String(commentId) });
  const headers = new Headers({ 'X-CSRFToken': getCSRFToken() });
  return POST(url, payload, { headers });
}
