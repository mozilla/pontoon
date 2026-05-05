import { asLocaleString } from './asLocaleString';

const LARGE_NUMBER = 1234567;
const RE_LATIN_DIGITS = /^\d[\d\W]*$/;

describe('asLocaleString', () => {
  it('always uses Latin digits regardless of locale', () => {
    expect(asLocaleString(LARGE_NUMBER, 'fa')).toMatch(RE_LATIN_DIGITS);
    expect(asLocaleString(LARGE_NUMBER, 'sat-Olck')).toMatch(RE_LATIN_DIGITS);
  });
  it('produces different output for different locale', () => {
    expect(asLocaleString(LARGE_NUMBER, 'en-GB')).not.toEqual(
      asLocaleString(LARGE_NUMBER, 'fr'),
    );
  });
});
