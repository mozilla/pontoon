import {
  isSelectMessage,
  parsePattern,
  type FormatKey,
  type Message,
  type Pattern,
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
  options: { escapeHTML: RegExp | null; trim: boolean } = {
    escapeHTML: null,
    trim: false,
  },
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

  const getPattern = (src: string, msg: Message): Pattern => {
    if (options.escapeHTML) {
      src = src.replace(options.escapeHTML, '&lt;$1');
    }
    if (options.trim) {
      src = src.trim();
    }
    return parsePattern(format, src, msg);
  };

  try {
    if (res.value) {
      setMessage(res.value, '', fields, getPattern);
    }
    if (res.attributes) {
      for (const [name, msg] of res.attributes) {
        setMessage(msg, name, fields, getPattern);
      }
    }
    return res;
  } catch {
    return null;
  }
}

/** Modifies `msg` according to `fields` entries which match `name`.  */
function setMessage(
  msg: Message,
  attrName: string,
  fields: EditorField[],
  getPattern: (src: string, msg: Message) => Pattern,
) {
  if (isSelectMessage(msg)) {
    msg.alt = [];
    for (const { name, keys, handle } of fields) {
      if (name === attrName) {
        const pat = getPattern(handle.current.value, msg);
        msg.alt.push({ keys, pat });
      }
    }
  } else {
    const body = Array.isArray(msg) ? msg : msg.msg;
    for (const { name, handle } of fields) {
      if (name === attrName) {
        const pat = getPattern(handle.current.value, msg);
        body.splice(0, body.length, ...pat);
        break;
      }
    }
  }
}
