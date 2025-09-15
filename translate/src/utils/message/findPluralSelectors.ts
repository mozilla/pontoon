import { CLDR_PLURALS } from '../constants';
import { isSelectMessage, type Message } from '@mozilla/l10n';

/**
 * Returns an array of selector indices for which the message
 * appears to contain a plural selector.
 */
export function findPluralSelectors(message: Message): Set<number> {
  const res = new Set<number>();
  if (isSelectMessage(message)) {
    const { sel: selectors, alt: variants } = message;
    for (let i = 0; i < selectors.length; ++i) {
      if (
        variants.every((v) => {
          const key = v.keys[i];
          const kv = typeof key === 'string' ? key : key['*'];
          return !kv || CLDR_PLURALS.includes(kv) || /^[0-9]+$/.test(kv);
        })
      ) {
        res.add(i);
      }
    }
  }
  return res;
}
