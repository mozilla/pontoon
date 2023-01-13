import type { MessageEntry } from '.';

import { parseEntry } from './parseEntry';

/**
 * Return a reconstructed Fluent message from the `original` message and some
 * `translation` content.
 *
 * @returns `null` if either the original or reconstructed message is not valid
 */
export function getReconstructedMessage(
  original: string,
  translation: string,
): MessageEntry | null {
  const message = parseEntry(original);
  if (!message) {
    console.error(
      new Error(`Error parsing '${original}' in getReconstructedMessage`),
    );
    return null;
  }
  let key = message.id;

  let content = `${key} =`;
  let indent = ' '.repeat(4);

  if (message.attributes?.size === 1) {
    const [attribute] = message.attributes.keys();
    content += `\n${indent}.${attribute} =`;
    indent = indent + indent;
  }

  if (translation.includes('\n')) {
    content += '\n' + translation.replace(/^/gm, indent);
  } else if (translation) {
    content += ' ' + translation;
  } else {
    content += ' { "" }';
  }

  return parseEntry(content);
}
