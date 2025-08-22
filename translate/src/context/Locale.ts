import { createContext } from 'react';
import { GET } from '~/api/utils/base';
import { keysToCamelCase } from '~/api/utils/keysToCamelCase';

export type Localization = Readonly<{
  project: Readonly<{ slug: string; name: string }>;
  totalStrings: number;
  approvedStrings: number;
  stringsWithWarnings: number;
}>;

export type Locale = Readonly<{
  code: string;
  name: string;
  cldrPlurals: readonly number[];
  pluralRule: string;
  direction: string;
  script: string;
  teamDescription: string;
  googleTranslateCode: string;
  msTranslatorCode: string;
  systranTranslateCode: string;
  msTerminologyCode: string;
  localizations: readonly Localization[];

  fetching: boolean;
  set: (locale: Locale) => void;
}>;

export const initLocale = (set: (locale: Locale) => void): Locale => ({
  code: '',
  name: '',
  cldrPlurals: [],
  pluralRule: '',
  direction: '',
  script: '',
  teamDescription: '',
  googleTranslateCode: '',
  msTranslatorCode: '',
  systranTranslateCode: '',
  msTerminologyCode: '',
  localizations: [],
  fetching: false,
  set,
});

export const Locale = createContext(initLocale(() => {}));

export async function updateLocale(locale: Locale, code: string) {
  const { set } = locale;
  set({ ...locale, fetching: true });

  let res = await GET(`/api/v2/locales/${code}`);

  res = keysToCamelCase(res);

  const next = res as Omit<Locale, 'cldrPlurals'> & {
    cldrPlurals: string;
  };
  const cldrPlurals = next.cldrPlurals
    .split(',')
    .map((i: string) => parseInt(i, 10));

  set({ ...next, cldrPlurals, fetching: false, set });
}
