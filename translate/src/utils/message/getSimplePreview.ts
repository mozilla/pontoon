import { serializeExpression } from '@fluent/syntax';
import { defaultFunctionMap, messageToFluent } from '@messageformat/fluent';
import type { Message } from 'messageformat';
import type { MessageEntry } from '.';
import { parseEntry } from './parseEntry';

/**
 * Turn a Fluent message into a simple string, without any syntax sigils.
 *
 * This function returns the most pertinent content that can be found in the
 * message, without the ID, attributes or selectors.
 *
 * For example:
 *   > my-message = Hello, World!
 *   "Hello, World!"
 *
 *   > my-selector =
 *   >     I like { $gender ->
 *   >        [male] him
 *   >        [female] her
 *   >       *[other] them
 *   >     }
 *   "I like them"
 *
 * @returns A simplified version of the `content`, or the original
 * if it isn't a valid Fluent message.
 */
export function getSimplePreview(content: string | MessageEntry): string {
  if (!content) {
    return '';
  }

  let entry: MessageEntry | null;
  if (typeof content === 'string') {
    entry = parseEntry(content);
    if (!entry) {
      return content;
    }
  } else {
    entry = content;
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

function previewMessage(message: Message): string {
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

  // TODO Should not be hard-coded
  const fnMap = { ...defaultFunctionMap, PLATFORM: 'PLATFORM' };
  const { elements } = messageToFluent(message, 'other', fnMap);

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
