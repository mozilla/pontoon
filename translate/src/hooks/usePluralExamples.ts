import { useMemo } from 'react';
import type { Locale } from '../../src/context/Locale';

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

    let found = 0;
    const examples: Record<number, number> = {};
    for (let n = 0; n < 1000; ++n) {
      if (found >= cldrPlurals.length) {
        return examples;
      }
      const rule = cldrPlurals[getRule(n)];
      if (!examples[rule]) {
        examples[rule] = n;
        found += 1;
      }
    }

    console.error('Unable to generate plural examples.');
    return examples;
  }, [locale]);
}
