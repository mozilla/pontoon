import { isSelectMessage, type Message } from '@mozilla/l10n';
import type { Locale } from '~/context/Locale';
import type { MessageEntry } from '.';
import { getEmptyMessageEntry } from './getEmptyMessage';
import { findPluralSelectors } from './findPluralSelectors';

/** Copy an entry using the plural categories of the destination locale. */
export function copyMessageEntry(
  source: MessageEntry,
  locale: Locale,
  original?: MessageEntry,
): MessageEntry {
  const template = structuredClone(source);
  if (
    source.value &&
    original?.value &&
    !isSelectMessage(source.value) &&
    findPluralSelectors(original.value).size
  ) {
    template.value = original.value;
  }
  if (source.attributes && template.attributes) {
    for (const [name, message] of source.attributes) {
      const reference = original?.attributes?.get(name);
      if (
        !isSelectMessage(message) &&
        reference &&
        findPluralSelectors(reference).size
      ) {
        template.attributes.set(name, reference);
      }
    }
  }
  const target = getEmptyMessageEntry(template, locale);
  if (source.value && target.value) {
    target.value = copyPatterns(source.value, target.value);
  }
  if (source.attributes && target.attributes) {
    for (const [name, message] of source.attributes) {
      target.attributes.set(
        name,
        copyPatterns(message, target.attributes.get(name)!),
      );
    }
  }
  return target;
}

function copyPatterns(source: Message, target: Message): Message {
  if (!isSelectMessage(source)) {
    if (isSelectMessage(target)) {
      const fallback = target.alt.find(({ keys }) =>
        keys.every((key) => typeof key !== 'string'),
      );
      if (fallback) {
        fallback.pat = structuredClone(
          Array.isArray(source) ? source : source.msg,
        );
      }
      if (!Array.isArray(source)) {
        Object.assign(target.decl, structuredClone(source.decl));
      }
      return target;
    }
    return structuredClone(source);
  }
  const plurals = findPluralSelectors(source);
  const select = isSelectMessage(target);
  const variants = select ? target.alt : [{ keys: [], pat: [] }];
  for (const variant of variants) {
    let candidates = source.alt;
    for (let i = 0; i < source.sel.length; ++i) {
      const index = select ? target.sel.indexOf(source.sel[i]) : -1;
      const key = index < 0 ? 'other' : variant.keys[index];
      const value = typeof key === 'string' ? key : key['*'];
      const exact = candidates.filter(({ keys }) => {
        const candidate = keys[i];
        return (
          (typeof candidate === 'string' ? candidate : candidate['*']) === value
        );
      });
      candidates =
        exact.length ||
        (plurals.has(i) && index >= 0 && typeof key === 'string')
          ? exact
          : candidates.filter(({ keys }) => typeof keys[i] !== 'string');
    }
    variant.pat = structuredClone(candidates[0]?.pat ?? []);
  }
  return select
    ? target
    : { decl: structuredClone(source.decl), msg: variants[0].pat };
}
