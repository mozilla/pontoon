/**
 * Adds `<span translate="no">` wrappers around `{braced}` content in `str`
 */
export function notranslateWrap(str: string): string {
  return str.replace(/{[^}]*}/g, '<span translate="no">$&</span>');
}

/**
 * Removes `<span translate="no">` wrappers from the input `str`
 */
export function notranslateUnwrap(str: string): string {
  return str.replace(/<span translate="no">(.*?)<\/span>/gs, '$1');
}
