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

export async function fetchAllLocales(): Promise<LocaleOption[]> {
  const search = new URLSearchParams({
    fields: 'code,name',
    page_size: '200',
    ordering: 'name',
  });
  const result = await GET('/api/v2/locales/', search);
  return Array.isArray(result?.results) ? result.results : [];
}
