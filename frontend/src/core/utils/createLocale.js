/* flow */

import type { Locale } from 'core/locale/actions';

const DEFAULT: Locale = {
    code: 'und',
    name: 'Unknown',
    cldrPlurals: [0],
    pluralRule: '',
    direction: 'ltr',
    script: 'Latn',
    googleTranslateCode: null,
    msTranslatorCode: null,
    systranTranslateCode: null,
    msTerminologyCode: null,
    localizations: [],
};

export default function createLocale(opts: $Shape<Locale>): Locale {
    const loc = Object.create(DEFAULT);
    Object.assign(loc, opts);
    return loc;
}
