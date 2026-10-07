import type { MessageEntry } from '.';
import { editablePattern } from './editablePattern';
import { entryPatterns } from './entryPatterns';

/** U+200F RIGHT-TO-LEFT MARK */
export const RLM = '\u200F';

/** U+200E LEFT-TO-RIGHT MARK */
export const LRM = '\u200E';

/** Strong right-to-left characters, including RLM and ALM */
const rtlChar =
  /[\u0590-\u08FF\u200F\uFB1D-\uFDFF\uFE70-\uFEFC\u{10800}-\u{10FFF}\u{1E800}-\u{1EFFF}]/u;

/** Any other letters, as well as LRM, are strong left-to-right characters */
const ltrChar = /[\p{L}\u200E]/u;

/** HTML/XML tags are not displayed, so they don't affect the direction */
const markup = /<\/?[a-z][^<>]*>/iy;

/**
 * Like UAX #9 rule P2, skip content between an isolate initiator
 * (LRI, RLI, FSI) and its matching PDI, or the end of the text.
 */
const isolate =
  /[\u2066-\u2068](?:[^\u2066-\u2069]|[\u2066-\u2068][^\u2069]*\u2069)*(?:\u2069|$)/uy;

/**
 * In an RTL locale, a translation that starts with LTR text (e.g. a placeholder)
 * is displayed with a left-to-right base direction, unless it starts with an RLM.
 *
 * Returns `true` if `text` needs a leading RLM: its first strong character
 * (skipping markup and isolates) is LTR, it contains some RTL characters,
 * and it does not start with an explicit LRM.
 *
 * Placeholders are not skipped, as they are not isolated in all contexts,
 * e.g. Firefox does not wrap Fluent placeables in FSI/PDI.
 *
 * https://github.com/mozilla/pontoon/issues/3236
 */
export function needsRtlMark(text: string): boolean {
  if (text.startsWith(LRM)) {
    return false;
  }
  let pos = 0;
  while (pos < text.length) {
    markup.lastIndex = pos;
    if (markup.test(text)) {
      pos = markup.lastIndex;
      continue;
    }
    isolate.lastIndex = pos;
    if (isolate.test(text)) {
      pos = isolate.lastIndex;
      continue;
    }
    const ch = String.fromCodePoint(text.codePointAt(pos)!);
    if (rtlChar.test(ch)) {
      return false;
    }
    if (ltrChar.test(ch)) {
      return rtlChar.test(text.slice(pos));
    }
    pos += ch.length;
  }
  return false;
}

/** Adds a leading RLM to `text`, if it needs one. */
export function addRtlMark(text: string): string {
  return needsRtlMark(text) ? RLM + text : text;
}

/**
 * Removes a leading RLM from `text`, if it would be added back by `addRtlMark()`.
 * This keeps the mark out of the editor, while preserving any other RLM.
 */
export function removeRtlMark(text: string): string {
  if (text.startsWith(RLM)) {
    const rest = text.slice(RLM.length);
    if (needsRtlMark(rest)) {
      return rest;
    }
  }
  return text;
}

/**
 * Adds a leading RLM to each pattern of `entry` that needs one, in place.
 * Used for messages edited as Fluent source, rather than as separate fields.
 */
export function addRtlMarks(entry: MessageEntry): MessageEntry {
  for (const pattern of entryPatterns(entry)) {
    if (needsRtlMark(editablePattern(entry.format, pattern))) {
      if (typeof pattern[0] === 'string') {
        pattern[0] = RLM + pattern[0];
      } else {
        pattern.unshift(RLM);
      }
    }
  }
  return entry;
}

/** Does `entry` have a pattern with a leading RLM that's added automatically? */
export function hasAddedRtlMark(entry: MessageEntry): boolean {
  for (const pattern of entryPatterns(entry)) {
    const text = editablePattern(entry.format, pattern);
    if (removeRtlMark(text) !== text) {
      return true;
    }
  }
  return false;
}
