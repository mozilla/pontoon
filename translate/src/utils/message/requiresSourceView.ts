import type { Message, PatternElement } from 'messageformat';
import type { MessageEntry } from '.';

const MAX_RICH_VARIANTS = 15;

const VALID_FUNCTIONS = [
  'DATETIME', // built-in DATETIME()
  'MESSAGE', // message & term references
  'NUMBER', // built-in NUMBER()
  'PLATFORM', // mozilla-central custom PLATFORM() selector
];

/** If `true`, the message can only be shown in a source editor.  */
export function requiresSourceView(entry: MessageEntry | null): boolean {
  if (!entry || !entry.id) {
    return true;
  }

  const { attributes, value } = entry;

  let fieldCount = 0;
  if (value) {
    if (messageContainsJunk(value)) {
      return true;
    }
    fieldCount = value.type === 'select' ? value.variants.length : 1;
  }

  if (attributes) {
    for (const attr of attributes.values()) {
      if (messageContainsJunk(attr)) {
        return true;
      }
      fieldCount += attr.type === 'select' ? attr.variants.length : 1;
    }
  }

  return fieldCount === 0 || fieldCount > MAX_RICH_VARIANTS;
}

function messageContainsJunk(message: Message | null): boolean {
  if (!message) {
    return false;
  }

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
    case 'expression':
      return !VALID_FUNCTIONS.includes(part.name);
    default:
      return false;
  }
}
