import type { Entry } from '@fluent/syntax';

import { parseEntry } from './parser';

/**
 * Return a reconstructed Fluent message from the original message and some
 * translated content.
 */
export function getReconstructedMessage(
  original: string,
  translation: string,
): Entry {
  const message = parseEntry(original);
  if (message.type !== 'Message' && message.type !== 'Term') {
    throw new Error(
      `Unexpected type '${message.type}' in getReconstructedMessage`,
    );
  }
  let key = message.id.name;

  // For Terms, the leading dash is removed in the identifier. We need to add
  // it back manually.
  if (message.type === 'Term') {
    key = '-' + key;
  }

  let content = `${key} =`;
  let indent = ' '.repeat(4);

  if (message.attributes && message.attributes.length === 1) {
    const attribute = message.attributes[0].id.name;
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
