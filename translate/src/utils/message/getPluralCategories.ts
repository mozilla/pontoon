import { CLDR_PLURALS } from '../constants';

export function getPluralCategories(code: string): Intl.LDMLPluralRule[] {
  // These special cases should be occasionally pruned on CLDR updates
  switch (code) {
    case 'tg': // Tajik
      return ['one', 'other'];
  }

  const pr = new Intl.PluralRules(code);
  const pc = pr.resolvedOptions().pluralCategories;
  pc.sort((a, b) =>
    CLDR_PLURALS.indexOf(a) < CLDR_PLURALS.indexOf(b) ? -1 : 1,
  );
  return pc;
}
