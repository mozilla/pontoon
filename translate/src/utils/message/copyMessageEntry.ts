import { isSelectMessage, type Message } from '@mozilla/l10n';
import type { Locale } from '~/context/Locale';
import type { MessageEntry } from '.';
import { getEmptyMessageEntry } from './getEmptyMessage';

/** Copy an entry using the plural categories of the destination locale. */
export function copyMessageEntry(
  source: MessageEntry,
  locale: Locale,
): MessageEntry {
  const target = getEmptyMessageEntry(source, locale);
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
    return structuredClone(source);
  }
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
      candidates = exact.length
        ? exact
        : candidates.filter(({ keys }) => typeof keys[i] !== 'string');
    }
    variant.pat = structuredClone(candidates[0]?.pat ?? []);
  }
  return select
    ? target
    : { decl: structuredClone(source.decl), msg: variants[0].pat };
}
