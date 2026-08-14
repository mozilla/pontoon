import {
  isSelectMessage,
  parsePattern,
  type FormatKey,
  type Message,
} from '@mozilla/l10n';
import type { EditorField } from '~/context/Editor';
import type { MessageEntry } from '.';

/**
 * Get a `MessageEntry` corresponding to `fields`, based on `base`.
 * Returns `null` on parse error.
 */
export function buildMessageEntry(
  base: MessageEntry,
  fields: EditorField[],
  options?: { trim: boolean },
): MessageEntry | null {
  const res = structuredClone(base);
  let format: FormatKey;
  switch (res.format) {
    case 'gettext':
      format = 'plain';
      break;
    case 'xcode':
      format = 'xliff';
      break;
    default:
      format = res.format ?? 'plain';
  }
  const trim = options?.trim ?? false;
  try {
    if (res.value) {
      setMessage(format, res.value, '', fields, trim);
    }
    if (res.attributes) {
      for (const [name, msg] of res.attributes) {
        setMessage(format, msg, name, fields, trim);
      }
    }
    return res;
  } catch {
    return null;
  }
}

/** Modifies `msg` according to `fields` entries which match `name`.  */
function setMessage(
  format: FormatKey,
  msg: Message,
  attrName: string,
  fields: EditorField[],
  trim: boolean,
) {
  if (isSelectMessage(msg)) {
    msg.alt = [];
    for (const { name, keys, handle } of fields) {
      if (name === attrName) {
        const value = handle.current.value;
        const pat = parsePattern(format, trim ? value.trim() : value, msg);
        msg.alt.push({ keys, pat });
      }
    }
  } else {
    const body = Array.isArray(msg) ? msg : msg.msg;
    for (const { name, handle } of fields) {
      if (name === attrName) {
        const value = handle.current.value;
        const pat = parsePattern(format, trim ? value.trim() : value, msg);
        body.splice(0, body.length, ...pat);
        break;
      }
    }
  }
}
