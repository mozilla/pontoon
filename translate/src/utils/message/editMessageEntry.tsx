import type { EditorField } from '~/context/Editor';
import type { MessageEntry } from '.';
import { findPluralSelectors } from './findPluralSelectors';
import { serializeEntry } from './serializeEntry';
import { CatchallKey, isSelectMessage, Message, Pattern } from '@mozilla/l10n';
import { androidEditPattern } from './android';

const emptyHandleRef = (value: string) => ({
  current: {
    value,
    focus() {},
    setSelection() {},
    setValue(text: string) {
      this.value = text;
    },
  },
});

/** Get an `EditorField[]` for the source view */
export function editSource(source: string | MessageEntry): EditorField[] {
  const value = typeof source === 'string' ? source : serializeEntry(source);
  const handle = emptyHandleRef(value.trim());
  return [{ id: '', name: '', keys: [], labels: [], handle }];
}

/** Get an `EditorField[]` corresponding to `entry`. */
export function editMessageEntry(entry: MessageEntry): EditorField[] {
  const res: EditorField[] = [];
  if (entry.value) {
    const hasAttributes = !!entry.attributes?.size;
    for (const [keys, labels, value] of genPatterns(
      entry.format,
      entry.value,
    )) {
      if (hasAttributes) {
        labels.unshift({ label: 'Value', plural: false });
      }
      const handle = emptyHandleRef(value);
      const id = getId('', keys);
      res.push({ handle, id, name: '', keys, labels });
    }
  }
  if (entry.attributes) {
    const hasMultiple = entry.attributes.size > 1 || !!entry.value;
    for (const [name, msg] of entry.attributes) {
      for (const [keys, labels, value] of genPatterns(entry.format, msg)) {
        if (hasMultiple) {
          labels.unshift({ label: name, plural: false });
        }
        const handle = emptyHandleRef(value);
        const id = getId(name, keys);
        res.push({ handle, id, name, keys, labels });
      }
    }
  }
  return res;
}

function* genPatterns(
  format: MessageEntry['format'],
  msg: Message,
): Generator<
  [(string | CatchallKey)[], Array<{ label: string; plural: boolean }>, string]
> {
  if (isSelectMessage(msg)) {
    const plurals = findPluralSelectors(msg);
    for (const { keys, pat } of msg.alt) {
      const labels = keys.map((key, i) => ({
        label: (typeof key === 'string' ? key : key['*']) || 'other',
        plural: plurals.has(i),
      }));
      yield [keys, labels, patternAsString(format, pat)];
    }
  } else {
    yield [[], [], patternAsString(format, Array.isArray(msg) ? msg : msg.msg)];
  }
}

export function patternAsString(
  format: MessageEntry['format'],
  pattern: Pattern,
) {
  if (format === 'android') return androidEditPattern(pattern);
  switch (pattern.length) {
    case 0:
      return '';
    case 1:
      if (typeof pattern[0] === 'string') return pattern[0];
      throw new Error('Unsupported message element');
  }
  throw new Error(`Unsupported message pattern length ${pattern.length}`);
}

function getId(name: string, keys: (string | CatchallKey)[]) {
  return [
    name,
    ...keys.map((key) => (typeof key === 'string' ? key : key['*'] || '*')),
  ].join('|');
}
