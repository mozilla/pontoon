import { fetchFluentTerms } from './fluentTerms';

import type { FluentTerms } from './fluentTerms';

export type GetFluentTerms = () => Promise<FluentTerms>;

export const termsCache = new Map<string, Promise<FluentTerms>>();

export function createGetFluentTerms(
  project: string,
  locale: string,
): GetFluentTerms {
  const key = `${project}/${locale}`;

  return () => {
    if (!termsCache.has(key)) {
      const terms = fetchFluentTerms(project, locale);
      termsCache.set(key, terms);
    }

    return termsCache.get(key)!;
  }
}
