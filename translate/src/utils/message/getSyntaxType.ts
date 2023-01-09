import type { Message, PatternElement } from 'messageformat';
import type { MessageEntry } from '.';

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
  if (!entry || !entry.id || messageContainsJunk(entry.value)) {
    return 'complex';
  }

  if (entry.attributes) {
    let hasSelect = false;
    for (const attr of entry.attributes.values()) {
      if (messageContainsJunk(attr)) {
        return 'complex';
      }
      hasSelect ||= attr.type === 'select';
    }
    const count = entry.attributes.size + (entry.value ? 1 : 0);
    if (hasSelect || count > 1) {
      return 'rich';
    }
  }

  return entry.value?.type === 'select' ? 'rich' : 'simple';
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
    default:
      return false;
  }
}
