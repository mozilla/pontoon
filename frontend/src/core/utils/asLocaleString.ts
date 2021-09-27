/**
 * Format number as a language-sensitive representation.
 * TODO: De-hardcode en-GB locale.
 * See https://github.com/mozilla/pontoon/issues/2168 for details.
 *
 * @param {number} number The number to be formatted.
 * @returns {string} A language-sensitive representation of the number.
 */
export default function asLocaleString(number: number): string {
    return Number(number).toLocaleString('en-GB');
}
