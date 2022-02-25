import { createContext } from 'react';
import APIBase from '~/core/api/base';

export type Localization = Readonly<{
  project: Readonly<{ slug: string; name: string }>;
  totalStrings: number;
  approvedStrings: number;
  stringsWithWarnings: number;
}>;

export type LocaleType = Readonly<{
  code: string;
  name: string;
  cldrPlurals: Array<number>;
  pluralRule: string;
  direction: string;
  script: string;
  googleTranslateCode: string;
  msTranslatorCode: string;
  systranTranslateCode: string;
  msTerminologyCode: string;
  localizations: Localization[];

  fetching: boolean;
  set: (locale: LocaleType) => void;
}>;

export const initLocale = (set: (locale: LocaleType) => void): LocaleType => ({
  code: '',
  name: '',
  cldrPlurals: [],
  pluralRule: '',
  direction: '',
  script: '',
  googleTranslateCode: '',
  msTranslatorCode: '',
  systranTranslateCode: '',
  msTerminologyCode: '',
  localizations: [],
  fetching: false,
  set,
});

export const Locale = createContext(initLocale(() => {}));

export async function updateLocale(locale: LocaleType, code: string) {
  const { set } = locale;
  set({ ...locale, fetching: true });

  const query = `{
    locale(code: "${code}") {
      code
      name
      cldrPlurals
      pluralRule
      direction
      script
      googleTranslateCode
      msTranslatorCode
      systranTranslateCode
      msTerminologyCode
      localizations {
        totalStrings
        approvedStrings
        stringsWithWarnings
        project {
          slug
          name
        }
      }
    }
  }`;

  const payload = new URLSearchParams();
  payload.append('query', query);
  const headers = new Headers();
  headers.append('X-Requested-With', 'XMLHttpRequest');
  const res = await new APIBase().fetch('/graphql', 'GET', payload, headers);

  const next = res.data.locale;
  next.cldrPlurals = next.cldrPlurals
    .split(',')
    .map((i: string) => parseInt(i, 10));
  next.direction = next.direction.toLowerCase();

  set({ ...next, fetching: false, set });
}
