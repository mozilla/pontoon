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

import type { MachineryAutocomplete } from '~/api/user';
import { placeholder } from '~/modules/placeable/placeholder';

export const MIN_MATCH_TO_COMPLETE_WORD = 4;

export const MIN_MATCH_TO_SUGGEST_NEXT_WORD = 8;

export const setGhostTextCandidates = StateEffect.define<readonly string[]>();

export const setGhostTextMode = StateEffect.define<MachineryAutocomplete>();

const dismissGhostTextEffect = StateEffect.define<null>();

type GhostTextState = {
  segmenter: Intl.Segmenter;
  candidates: readonly string[];
  mode: MachineryAutocomplete;
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
      } else if (effect.is(setGhostTextMode)) {
        next = { ...next, mode: effect.value };
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
    ghost.mode === 'off' ||
    ghost.dismissed ||
    ghost.candidates.length === 0 ||
    ranges.length > 1 ||
    !main.empty ||
    currentCompletions(state).length > 0
  ) {
    return null;
  }
  const pos = main.head;
  const line = state.doc.lineAt(pos);
  const full = ghost.mode === 'full' && pos === state.doc.length;
  const text = findGhostText(
    state.doc.sliceString(0, pos),
    line.text.slice(pos - line.from),
    ghost.candidates,
    ghost.segmenter,
    full,
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
          mode: 'word',
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
  const ghost = view.composing ? null : getGhostText(view);
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
  if (view.composing || !getGhostText(view)) {
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
  full = false,
): string {
  if (wordChar.test(after.charAt(0))) {
    return '';
  }

  let best = { candidate: '', length: 0 };
  for (const candidate of candidates) {
    const length = getMatchLength(before, candidate);
    if (length > best.length) {
      best = { candidate, length };
    }
  }

  const { candidate, length } = best;
  const match = before.slice(before.length - length);
  const weight = getMatchWeight(match);
  if (weight < MIN_MATCH_TO_COMPLETE_WORD) {
    return '';
  }
  const start = candidate.indexOf(match);
  const end = start + length;
  const unit = getUnitToComplete(
    candidate,
    start,
    end,
    weight,
    wordChar.test(before.charAt(before.length - length - 1)),
    segmenter,
  );
  if (!unit) {
    return '';
  }
  if (full) {
    return candidate.slice(end).replace(/\r\n?/g, '\n');
  }
  const text = candidate
    .slice(end, after ? unit.wordEnd : unit.end)
    .split(/[\r\n]/, 1)[0];
  return text.trim() && !after.startsWith(text) ? text : '';
}

function getUnitToComplete(
  candidate: string,
  start: number,
  end: number,
  weight: number,
  midWord: boolean,
  segmenter: Intl.Segmenter,
): Unit | null {
  const units = getUnits(candidate, segmenter);
  const current = units.find((u) => u.start < end && end < u.end);
  if (current && candidate.slice(end, current.end).trim()) {
    const aligned =
      start < current.start || (start === current.start && !midWord);
    return aligned ? current : null;
  }

  if (weight < MIN_MATCH_TO_SUGGEST_NEXT_WORD) {
    return null;
  }
  return units.find((u) => u.start >= end) ?? null;
}

/**
 * Letters of the scripts where one character is a whole syllable or
 * morpheme, so a 2-character word like 接続 or 연결 says about as much as
 * a 4-character word in Latin script.
 */
const denseScript =
  /[\p{scx=Han}\p{scx=Hiragana}\p{scx=Katakana}\p{scx=Hangul}\p{scx=Bopomofo}\p{scx=Yi}]/u;

function getMatchWeight(text: string): number {
  let weight = 0;
  for (const char of text) {
    weight +=
      hasWordChar.test(char) && denseScript.test(char) ? 2 : char.length;
  }
  return weight;
}

/**
 * What Tab accepts in word-by-word mode: a word with any punctuation,
 * placeholders or tags attached to it, and the space after it.
 * `wordEnd` is where its last word or placeholder ends.
 */
type Unit = { start: number; wordEnd: number; end: number };

const breakingSpace = /[^\S\u00a0\u2007\u202f]/;
const joiner = /^[-\u2010\u2011/\u00a0\u2007\u202f]+$/;

function getUnits(text: string, segmenter: Intl.Segmenter): Unit[] {
  const units: Unit[] = [];
  let unit: Unit | null = null;
  let hasWord = false;
  let joined: boolean | null = null;

  for (const token of tokenize(text, segmenter)) {
    const str = text.slice(token.start, token.end);
    if (!token.isWord && breakingSpace.test(str)) {
      if (unit) {
        const newline = str.search(/[\r\n]/);
        unit.end = newline === -1 ? token.end : token.start + newline;
        units.push(unit);
        unit = null;
      }
      continue;
    }

    const isText = token.isWord && !token.isPlaceholder;
    if (unit && isText && hasWord && !joined) {
      units.push(unit);
      unit = null;
    }
    if (!unit) {
      unit = { start: token.start, wordEnd: token.start, end: token.end };
      hasWord = false;
      joined = null;
    }
    unit.end = token.end;
    if (token.isWord) {
      unit.wordEnd = token.end;
    }
    if (isText) {
      hasWord = true;
      joined = null;
    } else {
      joined = (joined ?? true) && joiner.test(str);
    }
  }
  if (unit) {
    units.push(unit);
  }
  return units;
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

type Token = {
  start: number;
  end: number;
  isWord: boolean;
  isPlaceholder?: true;
};

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
      tokens.push({
        start: match.index,
        end: pos,
        isWord: true,
        isPlaceholder: true,
      });
    }
  }
  addSegments(pos, text.length);
  return tokens;
}
