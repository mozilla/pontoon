import type {
  CatchallKey,
  Message,
  PatternElement,
  PatternMessage,
  SelectMessage,
  Variant,
} from 'messageformat';

import type { Locale } from '~/context/Locale';
import { pojoCopy } from '../pojo';
import type { MessageEntry } from '.';
import { findPluralSelectors } from './findPluralSelectors';
import { getPluralCategories } from './getPluralCategories';

/**
 * Return a copy of a given MessageEntry with all its patterns empty.
 *
 * Declarations are preserved from the original Messages,
 * along with expression and variable selectors.
 * Plural categories are adjusted to match the given locale.
 * Select messages which would result in only one (default) variant
 * are returned as simple pattern messages instead.
 *
 * @param source An entry to use as template.
 * @param locale The target locale.
 * @returns An emptied copy of the source.
 */
export function getEmptyMessageEntry(
  source: MessageEntry,
  locale: Locale,
): MessageEntry {
  if (source.attributes) {
    const value = source.value ? getEmptyMessage(source.value, locale) : null;
    const attributes = new Map<string, Message>();
    for (const [key, message] of source.attributes) {
      attributes.set(key, getEmptyMessage(message, locale));
    }
    return { id: source.id, value, attributes };
  }
  return { id: source.id, value: getEmptyMessage(source.value, locale) };
}

function getEmptyMessage(
  source: Message,
  { code }: Locale,
): PatternMessage | SelectMessage {
  const declarations = pojoCopy(source.declarations);

  if (source.type === 'message' || source.type === 'junk') {
    return { type: 'message', declarations, pattern: { body: [] } };
  }

  const plurals = findPluralSelectors(source);
  const selectors: PatternElement[] = [];
  let variantKeys: Array<Variant['keys']> = [];
  for (let i = 0; i < source.selectors.length; ++i) {
    let sel = source.selectors[i];
    while (sel.type === 'placeholder') {
      sel = sel.body;
    }
    if (sel.type !== 'expression' && sel.type !== 'variable') {
      continue;
    }

    const keys: Variant['keys'] = [];
    let catchall: CatchallKey | null = null;
    if (plurals.includes(i)) {
      const exactKeys = new Set<string>();
      for (const v of source.variants) {
        const k = v.keys[i];
        if (k.type === '*') {
          catchall = { ...k };
        } else if (/^[0-9]+$/.test(k.value)) {
          exactKeys.add(k.value);
        }
      }
      for (const key of exactKeys) {
        keys.push({ type: 'nmtoken', value: key });
      }

      const pc = getPluralCategories(code);
      catchall = { type: '*', value: pc.pop() } as CatchallKey;
      for (const cat of pc) {
        keys.push({ type: 'nmtoken', value: cat });
      }
    } else {
      const keyValues = new Set<string>();
      for (const v of source.variants) {
        const k = v.keys[i];
        if (k.type === '*') {
          catchall = { ...k };
        } else if (!keyValues.has(k.value)) {
          keyValues.add(k.value);
          keys.push({ ...k });
        }
      }
    }

    if (keys.length > 0) {
      selectors.push(pojoCopy(sel));
      keys.push(catchall ?? { type: '*' });
      if (variantKeys.length === 0) {
        variantKeys = keys.map((key) => [key]);
      } else {
        const next: Array<Variant['keys']> = [];
        for (const vk of variantKeys) {
          for (const k of keys) {
            next.push([...vk, k]);
          }
        }
        variantKeys = next;
      }
    }
  }

  if (selectors.length === 0) {
    return { type: 'message', declarations, pattern: { body: [] } };
  }

  const variants = variantKeys.map((keys) => ({ keys, value: { body: [] } }));
  return { type: 'select', declarations, selectors, variants };
}
