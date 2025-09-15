import { CLDR_PLURALS } from '../constants';

export function getPluralCategories(code: string): Intl.LDMLPluralRule[] {
  // These special cases should be occasionally pruned on CLDR updates
  switch (new Intl.Locale(code).language) {
    case 'ace': // Acehnese
    case 'ilo': // Iloko
    case 'meh': // Mixteco Yucuhiti
    case 'mix': // Mixtepec Mixtec
    case 'pai': // Pai pai
      return ['other'];
    case 'tg': // Tajik
      return ['one', 'other'];
    case 'ltg': // Latgalian
      return ['zero', 'one', 'other'];

    // For the following, deliberately ignore the `other` rule for fractions
    case 'be': // Belarusian
    case 'pl': // Polish
    case 'ru': // Russian
    case 'szl': // Silesian
    case 'uk': // Ukrainian
      return ['one', 'few', 'many'];

    // For the following, deliberately ignore the `many` rule for millions
    case 'ca': // Catalan
    case 'es': // Spanish
    case 'fr': // French
    case 'it': // Italian
    case 'pt': // Portuguese
      return ['one', 'other'];
  }

  const supported = Intl.PluralRules.supportedLocalesOf(code);
  if (supported.length === 0) {
    return ['one', 'other'];
  }

  const pr = new Intl.PluralRules(code);
  const pc = pr.resolvedOptions().pluralCategories;
  pc.sort((a, b) =>
    CLDR_PLURALS.indexOf(a) < CLDR_PLURALS.indexOf(b) ? -1 : 1,
  );
  return pc;
}
