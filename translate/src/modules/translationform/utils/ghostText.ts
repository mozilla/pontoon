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

function getWordSegmenter(locale: string) {
  if (typeof Intl.Segmenter !== 'function') {
    return null;
  }
  try {
    return new Intl.Segmenter(locale, { granularity: 'word' });
  } catch {
    return new Intl.Segmenter(undefined, { granularity: 'word' });
  }
}

export const acceptGhostText: Command = (view) => {
  const ghost = getGhostText(view);
  if (!ghost) {
    return false;
  }
  const { pos, text } = ghost;
  view.dispatch({
    changes: { from: pos, insert: text },
    selection: { anchor: pos + text.length },
    scrollIntoView: true,
    userEvent: 'input.complete',
  });
  return true;
};
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
    if (hasWordChar.test(match[0])) {
      addSegments(pos, match.index);
      pos = match.index + match[0].length;
      tokens.push({ start: match.index, end: pos, isWord: true });
    }
  }
  addSegments(pos, text.length);
  return tokens;
}
