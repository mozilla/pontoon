import type { Message } from 'messageformat';
import type { EditorMessage } from '~/context/Editor';
import { pojoCopy } from '../pojo';
import type { MessageEntry } from '.';

/** Get a `MessageEntry` corresponding to `edit`, based on `base`. */
export function buildMessageEntry(
  base: MessageEntry,
  edit: EditorMessage,
): MessageEntry {
  const res = pojoCopy(base);
  setMessage(res.value, '', edit);
  if (res.attributes) {
    for (const [name, msg] of res.attributes) {
      setMessage(msg, name, edit);
    }
  }
  return res;
}

/** Modifies `msg` according to `edit` entries which match `name`.  */
function setMessage(msg: Message | null, name: string, edit: EditorMessage) {
  switch (msg?.type) {
    case 'message':
      for (const field of edit) {
        if (field.name === name) {
          const { body } = msg.pattern;
          if (body.length === 1 && body[0].type === 'text') {
            body[0].value = field.value;
          } else {
            body.splice(0, body.length, { type: 'text', value: field.value });
          }
          return;
        }
      }
      return;

    case 'select':
      msg.variants = [];
      for (const field of edit) {
        if (field.name === name) {
          msg.variants.push({
            keys: field.keys,
            value: { body: [{ type: 'text', value: field.value }] },
          });
        }
      }
      return;
  }

  return;
}
