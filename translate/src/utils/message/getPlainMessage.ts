import type { MessageEntry } from '.';
import { getSimplePreview } from './getSimplePreview';

/**
 * Return a plain string representation of a given message.
 *
 * @param format The format of the file of the concerned entity.
 * @returns If the format is Fluent (`'ftl'`), return a simplified
 *   version of the translation. Otherwise, return the original translation.
 */
export function getPlainMessage(
  message: string | MessageEntry,
  format: string,
): string {
  if (format === 'ftl' || typeof message !== 'string') {
    return getSimplePreview(message);
  }
  return message;
}
