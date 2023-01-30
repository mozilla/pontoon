import type { Message, PatternElement } from 'messageformat';
import type { MessageEntry } from '.';

const MAX_RICH_VARIANTS = 15;

/**
 * Return the syntax type of a given MessageEntry.
 *
 * @returns One of:
 *   - `'simple'`: can be shown as a simple string using the generic editor
 *   - `'rich'`: can be shown in a rich editor
 *   - `'complex'`: can only be shown in a source editor
 */
export function getSyntaxType(
  entry: MessageEntry | null,
): 'simple' | 'rich' | 'complex' {
  if (!entry || !entry.id) {
    return 'complex';
  }
  const { attributes, value } = entry;

  let fieldCount = 0;
  if (value) {
    if (messageContainsJunk(value)) {
      return 'complex';
    }
    fieldCount = value.type === 'select' ? value.variants.length : 1;
  }

  if (attributes) {
    for (const attr of attributes.values()) {
      if (messageContainsJunk(attr)) {
        return 'complex';
      }
      fieldCount += attr.type === 'select' ? attr.variants.length : 1;
    }
  }

  return fieldCount > MAX_RICH_VARIANTS
    ? 'complex'
    : fieldCount > 1
    ? 'rich'
    : 'simple';
}

function messageContainsJunk(message: Message): boolean {
  if (message.type === 'junk') {
    return true;
  }

  for (const { target, value } of message.declarations) {
    if (partContainsJunk(target) || partContainsJunk(value)) {
      return true;
    }
  }

  if (message.type === 'message') {
    return message.pattern.body.some(partContainsJunk);
  } else {
    return (
      message.selectors.some(partContainsJunk) ||
      message.variants.some(({ value }) => value.body.some(partContainsJunk))
    );
  }
}

function partContainsJunk(part: PatternElement): boolean {
  switch (part.type) {
    case 'junk':
      return true;
    case 'placeholder':
      return partContainsJunk(part.body);
    default:
      return false;
  }
}
