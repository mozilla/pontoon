import { Message, Pattern } from '@mozilla/l10n';
import type { MessageEntry } from '.';

export function* entryPatterns(entry: MessageEntry): IterableIterator<Pattern> {
  if (entry.value) {
    yield* msgPatterns(entry.value);
  }
  if (entry.attributes) {
    for (const msg of entry.attributes.values()) {
      yield* msgPatterns(msg);
    }
  }
}

function* msgPatterns(msg: Message) {
  if (Array.isArray(msg)) {
    yield msg;
  } else if (msg.msg) {
    yield msg.msg;
  } else {
    for (const v of msg.alt) {
      yield v.pat;
    }
  }
}
