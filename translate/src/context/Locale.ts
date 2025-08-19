import { createContext } from 'react';
import { GET } from '~/api/utils/base';

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

  let localizations = [];
  for (const project of res.projects) {
    const localization = await GET(`/api/v2/${code}/${project}`);
    localizations.push({
      totalStrings: localization.total_strings,
      approvedStrings: localization.approved_strings,
      stringsWithWarnings: localization.strings_with_warnings,
      project: { slug: project, name: localization.project.name },
    });
  }

  res = {
    code: res.code,
    name: res.name,
    cldrPlurals: res.cldr_plurals,
    pluralRule: res.plural_rule,
    direction: res.direction.toUpperCase(),
    script: res.script,
    teamDescription: res.team_description,
    googleTranslateCode: res.google_translate_code,
    msTranslatorCode: res.ms_translator_code,
    systranTranslateCode: res.systran_translate_code,
    msTerminologyCode: res.ms_terminology_code,
    localizations: localizations,
  };

  const next = res as Omit<Locale, 'cldrPlurals'> & {
    cldrPlurals: string;
  };
  const cldrPlurals = next.cldrPlurals
    .split(',')
    .map((i: string) => parseInt(i, 10));
  const direction = next.direction.toLowerCase();

  set({ ...next, cldrPlurals, direction, fetching: false, set });
}
