import { serializeExpression } from '@fluent/syntax';
import { messageToFluent } from '@messageformat/fluent';
import type { Model } from 'messageformat';
import type { MessageEntry } from '.';
import { parseEntry } from './parseEntry';

/**
 * Return a plain string representation of a given message.
 *
 * @param format The format of the file of the concerned entity.
 * @returns If the format is `'ftl'` or `'po'`, return a simplified
 *   version of the translation. Otherwise, return the original translation.
 */
export function getPlainMessage(
  message: string | MessageEntry,
  format: string,
): string {
  if (!message) {
    return '';
  }

  let entry: MessageEntry | null;
  if (typeof message === 'string') {
    entry = parseEntry(format, message);
    if (!entry) {
      return message;
    }
  } else {
    entry = message;
  }

  if (entry.value) {
    return previewMessage(entry.value);
  }

  if (entry.attributes) {
    for (const attr of entry.attributes.values()) {
      const preview = previewMessage(attr);
      if (preview) {
        return preview;
      }
    }
  }

  return '';
}

function previewMessage(message: Model.Message): string {
  // Presumes that the last variant is the most appropriate
  // to use as a generic representation of the message.
  if (message.type === 'select') {
    const vc = message.variants.length;
    if (vc) {
      const { value } = message.variants[vc - 1];
      message = {
        type: 'message',
        declarations: message.declarations,
        pattern: value,
      };
    }
  }

  const functionMap = new Proxy(
    {},
    { get: (_, prop) => String(prop).toUpperCase() },
  );
  const { elements } = messageToFluent(message, { functionMap });

  let res = '';
  for (const elt of elements) {
    if (elt.type === 'TextElement') {
      res += elt.value;
    } else {
      const expression = serializeExpression(elt.expression);
      if (expression !== '""') {
        res += `{ ${expression} }`;
      }
    }
  }
  return res;
}
