import type { LocaleType } from '~/context/locale';

const cache = new WeakMap<LocaleType, Record<number, number>>();

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
export function usePluralExamples(locale: LocaleType): Record<number, number> {
  const prev = cache.get(locale);
  if (prev) return prev;
  const examples = findPluralExamples(locale);
  cache.set(locale, examples);
  return examples;
}

function findPluralExamples({
  cldrPlurals,
  pluralRule,
}: LocaleType): Record<number, number> {
  if (cldrPlurals.length === 2) {
    const [one, other] = cldrPlurals;
    return { [one]: 1, [other]: 2 };
  }

  const getRule = new Function('n', `return ${pluralRule}`) as (
    n: number,
  ) => number | boolean;

  let found = 0;
  const examples: Record<number, number> = {};
  for (let n = 0; n < 1000; ++n) {
    if (found >= cldrPlurals.length) return examples;
    const rule = cldrPlurals[Number(getRule(n))];
    if (!examples[rule]) {
      examples[rule] = n;
      found += 1;
    }
  }

  console.error('Unable to generate plural examples.');
  return examples;
}
