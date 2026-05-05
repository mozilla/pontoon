/**
 * Format number as a language-sensitive representation.
 * Use locale's native separator style but still render Western Arabic (Latin) digits,
 * since this is used for UI stats counts rather than translated content.
 *
 * @param {number} number The number to be formatted.
 * @param {string} localeCode BCP 47 locale code, e.g. "de" or "nb-NO", falls back to "en-GB" if empty.
 * @returns {string} A language-sensitive representation of the number.
 */
export function asLocaleString(number: number, localeCode: string): string {
  return Number(number).toLocaleString(localeCode || 'en-GB', {
    numberingSystem: 'latn',
  });
}
