import { currentCompletions } from '@codemirror/autocomplete';
import { type Extension, StateEffect, StateField } from '@codemirror/state';
import {
  type Command,
  Decoration,
  type DecorationSet,
  EditorView,
  type KeyBinding,
  ViewPlugin,
  type ViewUpdate,
  WidgetType,
} from '@codemirror/view';

import { placeholder } from '~/modules/placeable/placeholder';
function getMatchLength(before: string, candidate: string): number {
  let min = 0;
  let max = Math.min(before.length, candidate.length);
  while (min < max) {
    const mid = Math.ceil((min + max) / 2);
    if (candidate.includes(before.slice(before.length - mid))) {
      min = mid;
    } else {
      max = mid - 1;
    }
  }
  return min;
}

type Token = { start: number; end: number; isWord: boolean };

function tokenize(text: string, segmenter: Intl.Segmenter): Token[] {
  const tokens: Token[] = [];
  const addSegments = (start: number, end: number) => {
    const segments = segmenter.segment(text.slice(start, end));
    for (const { index, segment, isWordLike } of segments) {
      const pos = start + index;
      tokens.push({
        start: pos,
        end: pos + segment.length,
        isWord: !!isWordLike,
      });
    }
  };

  let pos = 0;
  for (const match of text.matchAll(placeholder)) {
    // Spaces and punctuation are also matched, but the segmenter handles those.
    if (hasWordChar.test(match[0])) {
      addSegments(pos, match.index);
      pos = match.index + match[0].length;
      tokens.push({ start: match.index, end: pos, isWord: true });
    }
  }
  addSegments(pos, text.length);
  return tokens;
}
