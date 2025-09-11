import type { Locale } from '~/context/Locale';
import type { MessageEntry } from '.';
import { findPluralSelectors } from './findPluralSelectors';
import { getPluralCategories } from './getPluralCategories';
import type { CatchallKey, Message } from '@mozilla/l10n';

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

function getEmptyMessage(source: Message, { code }: Locale): Message {
  if (Array.isArray(source)) return [''];

  const decl = structuredClone(source.decl);
  if (source.msg) return { decl, msg: [''] };

  const sel: string[] = [];
  const plurals = findPluralSelectors(source);
  let variantKeys: (string | CatchallKey)[][] = [];
  for (let i = 0; i < source.sel.length; ++i) {
    let keys: (string | CatchallKey)[];
    if (plurals.has(i)) {
      const keyValues = source.alt
        .map((v) => {
          const key = v.keys[i];
          return typeof key === 'string' ? key : key['*'];
        })
        .filter((value) => value && /^[0-9]+$/.test(value))
        .concat(getPluralCategories(code));
      keys = Array.from(new Set(keyValues));
      keys.push({ '*': keys.pop() as string });
    } else {
      const keyValues = new Set<string>();
      let catchall: string | undefined;
      for (const v of source.alt) {
        const k = v.keys[i];
        if (typeof k === 'string') {
          keyValues.add(k);
        } else {
          catchall = k['*'] || 'other';
          keyValues.add(catchall);
        }
      }
      keys = Array.from(keyValues, (value) =>
        value === catchall ? { '*': value } : value,
      );
      if (catchall === undefined) keys.push({ '*': '' });
    }

    if (keys.length > 1) {
      sel.push(source.sel[i]);
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

  if (sel.length === 0) return { decl, msg: [''] };

  const alt = variantKeys.map((keys) => ({ keys, pat: [''] }));
  return { decl, sel: sel, alt };
}
