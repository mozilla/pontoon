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

export const MIN_MATCH_TO_COMPLETE_WORD = 4;

export const MIN_MATCH_TO_SUGGEST_NEXT_WORD = 8;

export const setGhostTextCandidates = StateEffect.define<readonly string[]>();

const dismissGhostTextEffect = StateEffect.define<null>();

type GhostTextState = {
  segmenter: Intl.Segmenter;
  candidates: readonly string[];
  dismissed: boolean;
};

const ghostTextState = StateField.define<GhostTextState | null>({
  create: () => null,
  update(value, tr) {
    if (!value) {
      return value;
    }
    let next = value;
    if (next.dismissed && (tr.docChanged || tr.selection)) {
      next = { ...next, dismissed: false };
    }
    for (const effect of tr.effects) {
      if (effect.is(setGhostTextCandidates)) {
        next = { ...next, candidates: effect.value };
      } else if (effect.is(dismissGhostTextEffect)) {
        next = { ...next, dismissed: true };
      }
    }
    return next;
  },
});

function getGhostText(view: EditorView): { pos: number; text: string } | null {
  const { state } = view;
  const ghost = state.field(ghostTextState, false);
  const { main, ranges } = state.selection;
  if (
    !ghost ||
    ghost.dismissed ||
    ghost.candidates.length === 0 ||
    ranges.length > 1 ||
    !main.empty ||
    view.composing ||
    currentCompletions(state).length > 0
  ) {
    return null;
  }
  const pos = main.head;
  const line = state.doc.lineAt(pos);
  const text = findGhostText(
    state.doc.sliceString(0, pos),
    line.text.slice(pos - line.from),
    ghost.candidates,
    ghost.segmenter,
  );
  return text ? { pos, text } : null;
}

class GhostTextWidget extends WidgetType {
  constructor(readonly text: string) {
    super();
  }

  eq(other: GhostTextWidget) {
    return other.text === this.text;
  }

  toDOM() {
    const span = document.createElement('span');
    span.className = 'ghost-text';
    span.setAttribute('aria-hidden', 'true');
    span.textContent = this.text;
    return span;
  }
}

function ghostTextDecorations(view: EditorView): DecorationSet {
  const ghost = getGhostText(view);
  if (!ghost) {
    return Decoration.none;
  }
  const widget = new GhostTextWidget(ghost.text);
  return Decoration.set(
    Decoration.widget({ widget, side: 1 }).range(ghost.pos),
  );
}

const ghostTextPlugin = ViewPlugin.fromClass(
  class {
    decorations: DecorationSet;

    constructor(view: EditorView) {
      this.decorations = ghostTextDecorations(view);
    }

    update(update: ViewUpdate) {
      this.decorations = ghostTextDecorations(update.view);
    }
  },
  { decorations: (plugin) => plugin.decorations },
);

export function ghostText(locale: string): Extension {
  const segmenter = getWordSegmenter(locale);
  return segmenter
    ? [
        ghostTextState.init(() => ({
          segmenter,
          candidates: [],
          dismissed: false,
        })),
        ghostTextPlugin,
      ]
    : [];
}

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
export const dismissGhostText: Command = (view) => {
  if (!getGhostText(view)) {
    return false;
  }
  view.dispatch({ effects: dismissGhostTextEffect.of(null) });
  return true;
};

export const ghostTextKeymap: readonly KeyBinding[] = [
  { key: 'Tab', run: acceptGhostText },
  { key: 'Escape', run: dismissGhostText },
];

const wordChar = /[\p{L}\p{M}\p{N}]/u;
const hasWordChar = /[\p{L}\p{N}]/u;

export function findGhostText(
  before: string,
  after: string,
  candidates: readonly string[],
  segmenter: Intl.Segmenter,
): string {
  if (wordChar.test(after.charAt(0))) {
    return '';
  }

  let best = { length: 0, text: '' };
  for (const candidate of candidates) {
    const length = getMatchLength(before, candidate);
    if (length >= MIN_MATCH_TO_COMPLETE_WORD && length > best.length) {
      const start = candidate.indexOf(before.slice(before.length - length));
      const text = getContinuation(
        candidate,
        start,
        start + length,
        wordChar.test(before.charAt(before.length - length - 1)),
        segmenter,
      );
      const line = text.split(/[\r\n]/, 1)[0];
      if (line.trim() && !after.startsWith(line)) {
        best = { length, text: line };
      }
    }
  }
  return best.text;
}

function getContinuation(
  candidate: string,
  start: number,
  end: number,
  midWord: boolean,
  segmenter: Intl.Segmenter,
): string {
  const tokens = tokenize(candidate, segmenter);
  const current = tokens.find((t) => t.start < end && end < t.end);
  if (current?.isWord) {
    const aligned =
      start < current.start || (start === current.start && !midWord);
    return aligned ? candidate.slice(end, current.end) : '';
  }

  if (end - start < MIN_MATCH_TO_SUGGEST_NEXT_WORD) {
    return '';
  }
  // With no further words, suggest any remaining punctuation.
  const next = tokens.find((t) => t.isWord && t.start >= end);
  return candidate.slice(end, next?.end).trimEnd();
}

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
