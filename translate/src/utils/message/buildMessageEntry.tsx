import type { EditorResult } from '~/context/Editor';
import type { MessageEntry } from '.';
import { isSelectMessage, type Message, type Pattern } from '@mozilla/l10n';

/** Get a `MessageEntry` corresponding to `edit`, based on `base`. */
export function buildMessageEntry(
  base: MessageEntry,
  next: EditorResult,
): MessageEntry {
  const res = structuredClone(base);
  if (res.value) setMessage(res.value, '', next);
  if (res.attributes) {
    for (const [name, msg] of res.attributes) {
      setMessage(msg, name, next);
    }
  }
  return res;
}

/** Modifies `msg` according to `edit` entries which match `name`.  */
function setMessage(msg: Message, attrName: string, next: EditorResult) {
  if (isSelectMessage(msg)) {
    msg.alt = [];
    for (const { name, keys, value } of next) {
      if (name === attrName) msg.alt.push({ keys, pat: [value] });
    }
  } else {
    const body = Array.isArray(msg) ? msg : msg.msg;
    for (const { name, value } of next) {
      if (name === attrName) {
        if (body.length === 1 && typeof body[0] === 'string') {
          body[0] = value;
        } else {
          body.splice(0, body.length, value);
        }
        break;
      }
    }
  }
}
