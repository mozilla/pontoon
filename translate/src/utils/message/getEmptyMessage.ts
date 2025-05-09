import type { Model } from 'messageformat';

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
    const attributes = new Map<string, Model.Message>();
    for (const [key, message] of source.attributes) {
      attributes.set(key, getEmptyMessage(message, locale));
    }
    return { id: source.id, value, attributes };
  }
  return { id: source.id, value: getEmptyMessage(source.value, locale) };
}

function getEmptyMessage(
  source: Model.Message,
  { code }: Locale,
): Model.Message {
  const declarations = pojoCopy(source.declarations);

  if (source.type === 'message') {
    return { type: 'message', declarations, pattern: [''] };
  }

  const plurals = findPluralSelectors(source);
  const selectors: Model.VariableRef[] = [];
  let variantKeys: Array<Model.Variant['keys']> = [];
  for (let i = 0; i < source.selectors.length; ++i) {
    let keys: Model.Variant['keys'];
    if (plurals.includes(i)) {
      const keyValues = source.variants
        .map((v) => v.keys[i].value as string)
        .filter((value) => value && /^[0-9]+$/.test(value))
        .concat(getPluralCategories(code));
      keys = Array.from(new Set(keyValues), (value) => ({
        type: 'literal',
        value,
      }));
      keys.at(-1)!.type = '*';
    } else {
      const keyValues = new Set<string>();
      let catchall: string | undefined;
      for (const v of source.variants) {
        const k = v.keys[i];
        if (k.type === '*') {
          catchall = k.value || 'other';
          keyValues.add(catchall);
        } else {
          keyValues.add(k.value);
        }
      }
      keys = Array.from(keyValues, (value) => ({
        type: value === catchall ? '*' : 'literal',
        value,
      }));
      if (catchall === undefined) {
        keys.push({ type: '*' });
      }
    }

    if (keys.length > 1) {
      const sel = source.selectors[i];
      selectors.push({ type: 'variable', name: sel.name });
      if (variantKeys.length === 0) {
        variantKeys = keys.map((key) => [key]);
      } else {
        const next: typeof variantKeys = [];
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
    return { type: 'message', declarations, pattern: [''] };
  }

  const variants = variantKeys.map((keys) => ({ keys, value: [''] }));
  return { type: 'select', declarations, selectors, variants };
}
