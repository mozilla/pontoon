import { isSelectMessage, type CatchallKey, type Message } from '@mozilla/l10n';
import type { EditorField } from '~/context/Editor';
import type { MessageEntry } from '.';
import { findPluralSelectors } from './findPluralSelectors';
import { editablePattern } from './editablePattern';
import { serializeEntry } from './serializeEntry';

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

/** One editable pattern of an entry, without an editor handle attached. */
export type MessagePattern = Omit<EditorField, 'handle'> & { value: string };

/**
 * Get an `EditorField[]` corresponding to the `source` and `target` entries.
 *
 * The presence of a value is determined solely by `source`,
 * while the set of attributes may also be extended by `target`.
 * The message values are determined by the `target` entry.
 * If `target` is not set, `source` message values are used.
 */
export function editMessageEntry(
  source: MessageEntry,
  target?: MessageEntry,
): EditorField[] {
  return messageEntryPatterns(source, target).map(({ value, ...field }) => ({
    ...field,
    handle: emptyHandleRef(value),
  }));
}

/**
 * Get the editable patterns of the `source` and `target` entries, in editor
 * order. Same shape as {@link editMessageEntry}, for read-only uses that don't
 * need an editor handle per pattern.
 */
export function messageEntryPatterns(
  source: MessageEntry,
  target?: MessageEntry,
): MessagePattern[] {
  const { format } = source;

  let value, attributes;
  if (target) {
    value = target.value;
    attributes = source.attributes
      ? new Map(
          Array.from(source.attributes.keys(), (key) => [key, [] as Message]),
        )
      : null;
    if (target.attributes) {
      attributes = attributes
        ? new Map([...attributes, ...target.attributes])
        : target.attributes;
    }
  } else {
    value = source.value;
    attributes = source.attributes;
  }

  const res: MessagePattern[] = [];
  if (source.value) {
    const hasAttributes = !!attributes?.size;
    for (const [keys, labels, editable] of genPatterns(format, value ?? [])) {
      if (hasAttributes) {
        labels.unshift({ label: 'Value', plural: false });
      }
      const id = getId('', keys);
      res.push({ id, name: '', keys, labels, value: editable });
    }
  }
  if (attributes) {
    const hasMultiple = attributes.size > 1 || !!source.value;
    for (const [name, msg] of attributes) {
      for (const [keys, labels, value] of genPatterns(format, msg)) {
        if (hasMultiple) {
          labels.unshift({ label: name, plural: false });
        }
        const id = getId(name, keys);
        res.push({ id, name, keys, labels, value });
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
      yield [keys, labels, editablePattern(format, pat)];
    }
  } else {
    yield [[], [], editablePattern(format, Array.isArray(msg) ? msg : msg.msg)];
  }
}

function getId(name: string, keys: (string | CatchallKey)[]) {
  return [
    name,
    ...keys.map((key) => (typeof key === 'string' ? key : key['*'] || '*')),
  ].join('|');
}
