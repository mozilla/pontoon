import {
  type Expression,
  type Markup,
  type Pattern,
  fluentSerializePattern,
  isExpression,
  mf2SerializePattern,
} from '@mozilla/l10n';
import type { MessageEntry } from '.';

export function editablePattern(
  format: MessageEntry['format'],
  pattern: Pattern,
): string {
  if (format === 'fluent') {
    return fluentSerializePattern(
      // Drop empty literals: { "" }
      pattern.filter((el) => typeof el === 'string' || el._ !== '' || el.fn),
      undefined,
      { escapeSyntax: false, onError: () => {} },
    );
  }

  let str = '';
  for (const part of pattern) {
    str += typeof part === 'string' ? part : editablePlaceholder(part);
  }
  // FIXME: https://bugzilla.mozilla.org/show_bug.cgi?id=2055465
  return format === 'properties' ? str.replaceAll('\r', '\\r') : str;
}

function editablePlaceholder(part: Expression | Markup): string {
  if (typeof part.attr?.source === 'string') {
    return part.attr.source;
  }
  if (isExpression(part)) {
    if (part.fn === 'html' && part._) {
      return part._; // android-only
    }
    if (part.fn === 'entity' && part.$) {
      return `&${part.$};`; // android-only
    }
  } else if (part.open || part.elem) {
    let str = `<${part.open ?? part.elem}`;
    if (part.opt) {
      for (const [name, val] of Object.entries(part.opt)) {
        const opt = typeof val === 'string' ? JSON.stringify(val) : '$' + val.$;
        str += ` ${name}=${opt}`;
      }
    }
    return str + (part.open ? '>' : ' />');
  } else if (part.close) {
    if (!part.opt || Object.keys(part.opt).length === 0) {
      return `</${part.close}>`;
    }
  }
  // Fallback; this is an error
  return mf2SerializePattern([part], false);
}
