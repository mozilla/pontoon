import type { Message } from 'messageformat';

import { CLDR_PLURALS } from '../constants';

/**
 * Returns an array of selector indices for which the message
 * appears to contain a plural selector.
 */
export function findPluralSelectors(message: Message): number[] {
  const res: number[] = [];
  if (message.type === 'select') {
    const { selectors, variants } = message;
    for (let i = 0; i < selectors.length; ++i) {
      if (
        variants.every((v) => {
          const key = v.keys[i];
          return (
            !key.value ||
            CLDR_PLURALS.includes(key.value) ||
            /^[0-9]+$/.test(key.value)
          );
        })
      ) {
        res.push(i);
      }
    }
  }
  return res;
}
