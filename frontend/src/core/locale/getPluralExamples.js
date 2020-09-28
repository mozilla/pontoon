/* @flow */

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
export default function getPluralExamples(locale: Locale) {
    const pluralsCount = locale.cldrPlurals.length;
    const examples = {};

    if (pluralsCount === 2) {
        examples[locale.cldrPlurals[0]] = 1;
        examples[locale.cldrPlurals[1]] = 2;
    } else {
        // This variable is used in the pluralRule we eval in the while block.
        let n = 0;
        while (Object.keys(examples).length < pluralsCount) {
            // This `eval` is not so much evil. The pluralRule we parse
            // comes from our database and is not a user input.
            // eslint-disable-next-line
            const rule = eval(locale.pluralRule);
            if (!examples[locale.cldrPlurals[rule]]) {
                examples[locale.cldrPlurals[rule]] = n;
            }
            n++;
        }
    }

    return examples;
}
