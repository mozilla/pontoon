import type { MessageEntry } from '.';

import { parseEntry } from './parseEntry';

/**
 * Return a reconstructed Fluent message from the original message and some
 * translated content.
 */
export function getReconstructedMessage(
  original: string,
  translation: string,
): MessageEntry {
  const message = parseEntry(original);
  if (!message) {
    throw new Error(`Error parsing '${original}' in getReconstructedMessage`);
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

  const res = parseEntry(content);
  if (!res) {
    throw new Error(`Error parsing '${content}' in getReconstructedMessage`);
  }
  return res;
}
