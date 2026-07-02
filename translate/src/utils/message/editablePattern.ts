import {
  Expression,
  isExpression,
  mf2SerializePattern,
  Markup,
  Pattern,
  fluentSerializePattern,
} from '@mozilla/l10n';

/**
 * @param format - Either a `MessageEntry['format']` or an `Entity.format`;
 *   only the `'fluent'` value gets special consideration.
 */
export function editablePattern(format: string, pattern: Pattern): string {
  if (format === 'fluent') {
    return fluentSerializePattern(pattern, {
      escapeSyntax: false,
      onError: () => {},
    });
  }

  let str = '';
  for (const part of pattern) {
    str += typeof part === 'string' ? part : editablePlaceholder(part);
  }
  return str;
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
