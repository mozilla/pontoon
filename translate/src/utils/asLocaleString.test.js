import { asLocaleString } from './asLocaleString';

// French (and other locales) use Unicode Character 202F "NARROW NO-BREAK SPACE"
// (U+202F) as a thousands separator. See:
// https://github.com/unicode-org/cldr/blob/24f92afa0b467992a503c17aec466cdabebab282/common/main/fr.xml#L7165
const NNBSP = '\u202f';

describe('asLocaleString', () => {
  it('formats numbers with language-sensitive separators', () => {
    expect(asLocaleString(1234567, 'en-GB')).toEqual('1,234,567');
    expect(asLocaleString(1234567, 'de')).toEqual('1.234.567');
    expect(asLocaleString(1234567, 'fr')).toEqual(`1${NNBSP}234${NNBSP}567`);
  });

  it('always uses Latin digits regardless of locale', () => {
    expect(asLocaleString(1234567, 'fa')).toMatch(/^[0-9,.\s${NNBSP}]+$/);
    expect(asLocaleString(1234567, 'sat-Olck')).toMatch(/^[0-9,.\s${NNBSP}]+$/);
  });
});
