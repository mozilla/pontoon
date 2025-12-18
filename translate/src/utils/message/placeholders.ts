import {
  Expression,
  isExpression,
  mf2SerializePattern,
  Markup,
  Pattern,
  Message,
} from '@mozilla/l10n';

export const placeholderFormats = new Set([
  'android',
  'webext',
  'xcode',
  'xliff',
]);

export function getPlaceholderMap(
  msg: Message,
): Map<string, Expression | Markup> | null {
  const placeholders = new Map<string, Expression | Markup>();
  if (Array.isArray(msg)) addPlaceholders(msg, placeholders);
  else if (msg.msg) addPlaceholders(msg.msg, placeholders);
  else for (const v of msg.alt) addPlaceholders(v.pat, placeholders);
  return placeholders.size ? placeholders : null;
}

function addPlaceholders(
  pattern: Pattern,
  placeholders: Map<string, Expression | Markup>,
): void {
  for (const part of pattern) {
    if (typeof part !== 'string') {
      placeholders.set(editablePlaceholder(part), part);
    }
  }
}

export function editablePattern(pattern: Pattern): string {
  let str = '';
  for (const part of pattern) {
    str += typeof part === 'string' ? part : editablePlaceholder(part);
  }
  return str;
}

function editablePlaceholder(part: Expression | Markup): string {
  if (typeof part.attr?.source === 'string') return part.attr.source;
  if (isExpression(part)) {
    if (part.fn === 'html' && part._) return part._; // android-only
    if (part.fn === 'entity' && part.$) return `&${part.$};`; // android-only
  } else if (part.open || part.elem) {
    let str = `<${part.open ?? part.elem}`;
    if (part.opt) {
      for (const [name, val] of Object.entries(part.opt)) {
        const opt = typeof val === 'string' ? JSON.stringify(val) : '$' + val.$;
        str += ` ${name}=${opt}}`;
      }
    }
    return str + (part.open ? '>' : ' />');
  } else if (part.close) {
    if (!part.opt || Object.keys(part.opt).length === 0)
      return `</${part.close}>`;
  }
  // Fallback; this is an error
  return mf2SerializePattern([part], false);
}
