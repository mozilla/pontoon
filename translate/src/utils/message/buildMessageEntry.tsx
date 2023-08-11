import type { Message } from 'messageformat';
import type { EditorResult } from '~/context/Editor';
import { pojoCopy } from '../pojo';
import type { MessageEntry } from '.';

/** Get a `MessageEntry` corresponding to `edit`, based on `base`. */
export function buildMessageEntry(
  base: MessageEntry,
  next: EditorResult,
): MessageEntry {
  const res = pojoCopy(base);
  setMessage(res.value, '', next);
  if (res.attributes) {
    for (const [name, msg] of res.attributes) {
      setMessage(msg, name, next);
    }
  }
  return res;
}

/** Modifies `msg` according to `edit` entries which match `name`.  */
function setMessage(msg: Message | null, attrName: string, next: EditorResult) {
  switch (msg?.type) {
    case 'message':
      for (const { name, value } of next) {
        if (name === attrName) {
          const { body } = msg.pattern;
          if (body.length === 1 && body[0].type === 'text') {
            body[0].value = value;
          } else {
            body.splice(0, body.length, { type: 'text', value });
          }
          return;
        }
      }
      return;

    case 'select':
      msg.variants = [];
      for (const { name, keys, value } of next) {
        if (name === attrName) {
          msg.variants.push({
            keys,
            value: { body: [{ type: 'text', value }] },
          });
        }
      }
      return;
  }

  return;
}
