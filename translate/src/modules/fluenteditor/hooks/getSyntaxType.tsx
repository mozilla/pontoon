import type { Translation } from '~/core/editor';
import {
  getSyntaxType as getFluentSyntaxType,
  parseEntry,
} from '~/core/utils/fluent';
import type { SyntaxType } from '~/core/utils/fluent/types';

/**
 * Function to analyze a translation and determine what its appropriate syntax is.
 *
 * @returns The syntax of the translation, can be "simple", "rich" or "complex".
 *      - "simple" if the translation can be shown as a simple preview
 *      - "rich" if the translation is not simple but can be handled by the Rich editor
 *      - "complex" otherwise
 */

export function getSyntaxType(source: string | Translation): SyntaxType {
  if (source && typeof source !== 'string') {
    return getFluentSyntaxType(source);
  }

  const message = parseEntry(source);
  return message.type === 'Junk' ? 'simple' : getFluentSyntaxType(message);
}
