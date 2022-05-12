import { GET } from './utils/base';
import { keysToCamelCase } from './utils/keysToCamelCase';

/**
 * Term entry with translation.
 */
export type TermType = {
  readonly text: string;
  readonly partOfSpeech: string;
  readonly definition: string;
  readonly usage: string;
  readonly translation: string;
  readonly entityId: number;
};

export async function fetchTerms(
  sourceString: string,
  locale: string,
): Promise<TermType[]> {
  const search = new URLSearchParams({ source_string: sourceString, locale });
  const results = await GET('/terminology/get-terms/', search, {
    singleton: true,
  });
  return Array.isArray(results) ? keysToCamelCase(results) : [];
}
