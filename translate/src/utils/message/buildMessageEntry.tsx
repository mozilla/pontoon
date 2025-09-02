import type { Model } from 'messageformat';
import type { EditorResult } from '~/context/Editor';
import type { MessageEntry } from '.';

/** Get a `MessageEntry` corresponding to `edit`, based on `base`. */
export function buildMessageEntry(
  base: MessageEntry,
  next: EditorResult,
): MessageEntry {
  const res = structuredClone(base);
  setMessage(res.value, '', next);
  if (res.attributes) {
    for (const [name, msg] of res.attributes) {
      setMessage(msg, name, next);
    }
  }
  return res;
}

/** Modifies `msg` according to `edit` entries which match `name`.  */
function setMessage(
  msg: Model.Message | null,
  attrName: string,
  next: EditorResult,
) {
  switch (msg?.type) {
    case 'message':
      for (const { name, value } of next) {
        if (name === attrName) {
          const body = msg.pattern;
          if (body.length === 1 && typeof body[0] === 'string') {
            body[0] = value;
          } else {
            body.splice(0, body.length, value);
          }
          return;
        }
      }
      return;

    case 'select':
      msg.variants = [];
      for (const { name, keys, value } of next) {
        if (name === attrName) {
          msg.variants.push({ keys, value: [value] });
        }
      }
      return;
  }

  return;
}
