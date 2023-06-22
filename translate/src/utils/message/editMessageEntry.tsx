import type { Message, Pattern, Variant } from 'messageformat';
import type { EditorMessage } from '~/context/Editor';
import type { MessageEntry } from '.';
import { findPluralSelectors } from './findPluralSelectors';

/** Get an `EditorMessage` corresponding to `entry`. */
export function editMessageEntry(entry: MessageEntry): EditorMessage {
  const res: EditorMessage = [];
  if (entry.value) {
    const hasAttributes = !!entry.attributes?.size;
    for (const [keys, labels, value] of genPatterns(entry.value)) {
      if (hasAttributes) {
        labels.unshift({ label: 'Value', plural: false });
      }
      res.push({ id: getId('', keys), name: '', keys, labels, value });
    }
  }
  if (entry.attributes) {
    const hasMultiple = entry.attributes.size > 1 || !!entry.value;
    for (const [name, msg] of entry.attributes) {
      for (const [keys, labels, value] of genPatterns(msg)) {
        if (hasMultiple) {
          labels.unshift({ label: name, plural: false });
        }
        res.push({ id: getId(name, keys), name, keys, labels, value });
      }
    }
  }
  return res;
}

function* genPatterns(
  msg: Message,
): Generator<
  [Variant['keys'], Array<{ label: string; plural: boolean }>, string]
> {
  switch (msg.type) {
    case 'message':
      yield [[], [], patternAsString(msg.pattern)];
      break;
    case 'select': {
      const plurals = findPluralSelectors(msg);
      for (const { keys, value } of msg.variants) {
        const labels = keys.map((key, i) => ({
          label: key.value || 'other',
          plural: plurals.includes(i),
        }));
        yield [keys, labels, patternAsString(value)];
      }
      break;
    }
  }
}

function patternAsString({ body }: Pattern) {
  switch (body.length) {
    case 0:
      return '';
    case 1:
      if (body[0].type === 'text') {
        return body[0].value;
      } else {
        throw new Error(`Unsupported message element ${body[0].type}`);
      }
  }
  throw new Error(`Unsupported message pattern length ${body.length}`);
}

function getId(name: string, keys: Variant['keys']) {
  let id = name;
  for (const key of keys) {
    id += '|' + ('value' in key ? key.value : '*');
  }
  return id;
}
