import { GET } from './utils/base';

/*
 * Translation of an entity in a locale other than the currently selected locale.
 */
export type OtherLocaleTranslation = {
  readonly locale: {
    readonly code: string;
    readonly name: string;
    readonly pk: number;
    readonly direction: string;
    readonly script: string;
  };
  readonly translation: string;
  readonly is_preferred: boolean | null | undefined;
};

export type LocaleOption = {
  code: string;
  name: string;
};

export async function fetchOtherLocales(
  entity: number,
  locale: string,
): Promise<OtherLocaleTranslation[]> {
  const search = new URLSearchParams({ entity: String(entity), locale });
  const results = await GET('/other-locales/', search, { singleton: true });
  return Array.isArray(results) ? results : [];
}

export async function fetchAllLocales(slug: string): Promise<LocaleOption[]> {
  if (slug === 'all-projects') {
    const locales: LocaleOption[] = [];
    let url: string | null = '/api/v2/locales/?fields=code,name&ordering=name';
    while (url) {
      const result = await GET(url);
      if (Array.isArray(result?.results)) {
        locales.push(...result.results);
      }
      url = result?.next ?? null;
    }
    return locales;
  }

  const search = new URLSearchParams({ fields: 'localizations' });
  const url = `/api/v2/projects/${slug}/?${search}`;
  const result = await GET(url);
  const locales: LocaleOption[] = (result?.localizations ?? []).map(
    (l: { locale: LocaleOption }) => l.locale,
  );
  return locales;
}
