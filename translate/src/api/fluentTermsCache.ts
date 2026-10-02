import { fetchFluentTerms } from './fluentTerms';

import type { FluentTerms } from './fluentTerms';

export const termsCache = new Map<string, Promise<FluentTerms>>();

export async function getFluentTerms(
  project: string,
  locale: string,
): Promise<FluentTerms> {
  const key = `${project}/${locale}`;
  if (!termsCache.has(key)) {
    const terms = fetchFluentTerms(project, locale);
    termsCache.set(key, terms);
  }

  return termsCache.get(key)!;
}
