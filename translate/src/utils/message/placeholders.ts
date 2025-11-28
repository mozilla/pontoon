import {
  Expression,
  isExpression,
  mf2SerializePattern,
  Markup,
  Pattern,
  Message,
} from '@mozilla/l10n';
import type { MessageEntry } from '.';

export function getPlaceholderMap(
  format: MessageEntry['format'],
  msg: Message,
): Map<string, Expression | Markup> | null {
  const placeholders = new Map<string, Expression | Markup>();
  if (Array.isArray(msg)) addPlaceholders(format, msg, placeholders);
  else if (msg.msg) addPlaceholders(format, msg.msg, placeholders);
  else for (const v of msg.alt) addPlaceholders(format, v.pat, placeholders);
  return placeholders.size ? placeholders : null;
}

function addPlaceholders(
  format: string,
  pattern: Pattern,
  placeholders: Map<string, Expression | Markup>,
): void {
  for (const part of pattern) {
    if (typeof part !== 'string') {
      placeholders.set(editablePlaceholder(format, part), part);
    }
  }
}

export function editablePattern(
  format: MessageEntry['format'],
  pattern: Pattern,
): string {
  let str = '';
  for (const part of pattern) {
    str += typeof part === 'string' ? part : editablePlaceholder(format, part);
  }
  return str;
}

function editablePlaceholder(
  format: string,
  part: Expression | Markup,
): string {
  if (typeof part.attr?.source === 'string') return part.attr.source;
  if (format === 'android') {
    if (isExpression(part)) {
      if (part.fn === 'html' && part._) return part._;
      if (part.fn === 'entity' && part.$) return `&${part.$};`;
    } else if (part.open) {
      let str = `<${part.open}`;
      if (part.opt) {
        for (const [name, val] of Object.entries(part.opt)) {
          const opt =
            typeof val === 'string' ? JSON.stringify(val) : '$' + val.$;
          str += ` ${name}=${opt}}`;
        }
      }
      return str + '>';
    } else if (part.close) {
      if (!part.opt || Object.keys(part.opt).length === 0)
        return `</${part.close}>`;
    }
  }
  // Fallback; this is an error
  return mf2SerializePattern([part], false);
}
