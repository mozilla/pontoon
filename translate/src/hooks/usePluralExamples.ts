import { useMemo } from 'react';
import type { Locale } from '~/context/Locale';

/**
 * A map of examples for the current locale's cldrPlurals.
 *
 * For example, for Slovenian (sl) the function returns the following:
 *     {
 *          1: 1,
 *          2: 2,
 *          3: 3,
 *          5: 0,
 *     }
 *
 * @returns A map of locale's cldrPlurals and their plural examples.
 */
export function usePluralExamples(locale: Locale): Record<number, number> {
  return useMemo(() => {
    const { cldrPlurals, pluralRule } = locale;
    if (cldrPlurals.length === 2) {
      const [one, other] = cldrPlurals;
      return { [one]: 1, [other]: 2 };
    }

    const fnBody = `return Number(${pluralRule})`;
    const getRule = new Function('n', fnBody) as (n: number) => number;

    // The CLDR `many` category of languages such as Breton only matches
    // multiples of a million, which a 0..999 scan can never reach.
    const candidates = [...Array(1000).keys(), 1_000_000];

    let found = 0;
    const examples: Record<number, number> = {};
    for (const n of candidates) {
      const rule = cldrPlurals[getRule(n)];
      // `rule in examples` rather than a truthiness check, as 0 is a valid
      // example and would otherwise be treated as "not yet found".
      if (!(rule in examples)) {
        examples[rule] = n;
        // Checked here rather than at the top of the loop, so that a set
        // completed by the last candidate is not reported as a failure.
        if (++found >= cldrPlurals.length) {
          return examples;
        }
      }
    }

    console.error('Unable to generate plural examples.');
    return examples;
  }, [locale]);
}
