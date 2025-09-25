import type { EditorResult } from '~/context/Editor';
import type { MessageEntry } from '.';
import {
  Expression,
  isSelectMessage,
  Markup,
  type Message,
  type Pattern,
} from '@mozilla/l10n';

/** Get a `MessageEntry` corresponding to `edit`, based on `base`. */
export function buildMessageEntry(
  base: MessageEntry,
  placeholders: Map<string, Expression | Markup> | null,
  next: EditorResult,
): MessageEntry {
  const res = structuredClone(base);
  if (res.value) setMessage(res.value, '', placeholders, next);
  if (res.attributes) {
    for (const [name, msg] of res.attributes) {
      setMessage(msg, name, placeholders, next);
    }
  }
  return res;
}

/** Modifies `msg` according to `edit` entries which match `name`.  */
function setMessage(
  msg: Message,
  attrName: string,
  placeholders: Map<string, Expression | Markup> | null,
  next: EditorResult,
) {
  if (isSelectMessage(msg)) {
    msg.alt = [];
    for (const { name, keys, value } of next) {
      if (name === attrName) {
        const pat = buildPattern(value, placeholders);
        msg.alt.push({ keys, pat });
      }
    }
  } else {
    const body = Array.isArray(msg) ? msg : msg.msg;
    for (const { name, value } of next) {
      if (name === attrName) {
        const pat = buildPattern(value, placeholders);
        body.splice(0, body.length, ...pat);
        break;
      }
    }
  }
}

function buildPattern(
  str: string,
  placeholders: Map<string, Expression | Markup> | null,
): Pattern {
  if (!placeholders?.size) return [str];
  const replacements: {
    start: number;
    end: number;
    part: Expression | Markup;
  }[] = [];
  for (const [ph, part] of placeholders) {
    let i = str.indexOf(ph);
    while (i !== -1) {
      const end = i + ph.length;
      replacements.push({ start: i, end, part });
      i = str.indexOf(ph, end);
    }
  }
  replacements.sort((a, b) => a.start - b.start);
  const pattern: Pattern = [];
  let pos = 0;
  for (const { start, end, part } of replacements) {
    if (start < pos) continue;
    if (start > pos) pattern.push(str.substring(pos, start));
    pattern.push(part);
    pos = end;
  }
  if (pos < str.length) pattern.push(str.substring(pos));
  return pattern;
}
