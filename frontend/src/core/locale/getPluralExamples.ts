import type { Locale } from './actions';

/**
 * Return a map of given locale's cldrPlurals and their plural examples.
 *
 * For example, for Slovenian (sl) the function returns the following:
 *     {
 *          1: 1,
 *          2: 2,
 *          3: 3,
 *          5: 0,
 *     }
 *
 * @param {Locale} locale A Locale object.
 * @returns {Object} A map of locale's cldrPlurals and their plural examples.
 */
export default function getPluralExamples(
    locale: Locale,
): Record<number, number> {
    const pluralsCount = locale.cldrPlurals.length;
    const examples = {};

    if (pluralsCount === 2) {
        examples[locale.cldrPlurals[0]] = 1;
        examples[locale.cldrPlurals[1]] = 2;
    } else {
        const getRule = new Function('n', `return ${locale.pluralRule}`) as (
            n: number,
        ) => number | boolean;
        let n = 0;
        while (Object.keys(examples).length < pluralsCount) {
            const rule = locale.cldrPlurals[Number(getRule(n))];
            if (!examples[rule]) {
                examples[rule] = n;
            }
            n++;
            // Protection against infinite loop
            if (n === 1000) {
                console.error('Unable to generate plural examples.');
                break;
            }
        }
    }

    return examples;
}
