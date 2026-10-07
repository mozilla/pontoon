import { type Text, Transaction } from '@codemirror/state';
import {
  type Decoration,
  EditorView,
  type Rect,
  ViewPlugin,
  type ViewUpdate,
} from '@codemirror/view';

/** How close (in px) typed text should be to the clicked character next to it */
const NEAR = 5;

/** The furthest (in px) from the clicked character that's better than the default */
const FAR = 12;

type Click = { x: number; y: number; pos: number; doc: Text };

/**
 * In bidirectional text, a single point on screen may correspond to two
 * positions in the text, e.g. at the boundary of an English word in RTL text.
 * Which one shows typed text at that point depends on the direction of
 * the typed text, which is not known yet when clicking.
 *
 * So when text is typed right after a click, insert it at whichever of
 * the positions near the clicked point actually displays it next to
 * the clicked character. This is measured from the rendered result,
 * so it also accounts for the isolated placeholders, tags and quoted literals.
 *
 * This is done on `beforeinput`, while the DOM still matches the editor state.
 *
 * Native editors resolve this ambiguity by the direction of the keyboard
 * language, as that's what the next typed character is expected to be:
 * https://learn.microsoft.com/en-us/archive/blogs/murrays/text-insertion-point
 * Web pages can't detect that, so the typed character itself is used instead.
 *
 * https://github.com/mozilla/pontoon/issues/2985
 */
export const bidiTyping = ViewPlugin.fromClass(
  class {
    click: Click | null = null;

    update(update: ViewUpdate) {
      if (
        update.docChanged ||
        (update.selectionSet &&
          !update.transactions.some((tr) => tr.isUserEvent('select.pointer')))
      ) {
        this.click = null;
      }
    }
  },
  {
    eventHandlers: {
      click(event, view) {
        const { main, ranges } = view.state.selection;
        this.click =
          event.detail === 1 &&
          !event.shiftKey &&
          ranges.length === 1 &&
          main.empty
            ? {
                x: event.clientX,
                y: event.clientY,
                pos: main.head,
                doc: view.state.doc,
              }
            : null;
      },

      beforeinput(event, view) {
        const { click } = this;
        this.click = null;
        const { main, ranges } = view.state.selection;
        if (
          !click ||
          event.inputType !== 'insertText' ||
          !event.data ||
          event.isComposing ||
          view.composing ||
          ranges.length > 1 ||
          !main.empty ||
          main.head !== click.pos ||
          view.state.doc !== click.doc
        ) {
          return false;
        }
        const text = event.data;
        const pos = findInsertPosition(view, click, text);
        if (pos === null) {
          return false;
        }
        event.preventDefault();
        view.dispatch({
          changes: { from: pos, insert: text },
          selection: { anchor: pos + text.length },
          userEvent: 'input.type',
          scrollIntoView: true,
        });
        return true;
      },
    },
  },
);

/**
 * Returns a better position than `click.pos` for inserting `text`,
 * or `null` if there isn't one.
 */
function findInsertPosition(
  view: EditorView,
  click: Click,
  text: string,
): number | null {
  // Without any direction changes on the line, there's no ambiguity
  if (view.bidiSpans(view.state.doc.lineAt(click.pos)).length < 2) {
    return null;
  }
  const neighbours = getNeighbours(view, click);
  if (!neighbours.left.length && !neighbours.right.length) {
    return null;
  }
  const candidates = getCandidates(view, click, neighbours);
  if (candidates.length < 2) {
    return null;
  }

  // Try out each candidate, without adding them to the undo history.
  // The first one is the clicked position, which is kept if it's good enough.
  const trial = Transaction.addToHistory.of(false);
  let best = click.pos;
  let bestDist = Infinity;
  for (const pos of candidates) {
    view.dispatch({ changes: { from: pos, insert: text }, annotations: trial });
    const dist = distanceFromClick(view, click, neighbours, pos, text.length);
    view.dispatch({
      changes: { from: pos, to: pos + text.length },
      annotations: trial,
    });
    if (pos === click.pos && dist <= NEAR) {
      break;
    }
    if (dist < bestDist) {
      best = pos;
      bestDist = dist;
    }
  }
  view.dispatch({ selection: { anchor: click.pos }, annotations: trial });

  // Some places can't be reached exactly, as e.g. an English letter typed
  // between two English words in RTL text joins them. Then accept a close one.
  return best !== click.pos && bestDist <= FAR ? best : null;
}

/**
 * The characters displayed nearest to the click on its left and right,
 * nearest first, with their positions on screen.
 */
type Neighbour = { pos: number; rect: Rect };
type Neighbours = { left: Neighbour[]; right: Neighbour[] };

function getNeighbours(view: EditorView, click: Click): Neighbours {
  const line = view.state.doc.lineAt(click.pos);
  const res: Neighbours = { left: [], right: [] };
  for (let pos = line.from; pos < line.to; ++pos) {
    const rect = charRect(view, pos, click.y);
    if (rect) {
      const mid = (rect.left + rect.right) / 2;
      (mid <= click.x ? res.left : res.right).push({ pos, rect });
    }
  }
  const dist = (n: Neighbour) =>
    Math.abs((n.rect.left + n.rect.right) / 2 - click.x);
  res.left = res.left.sort((a, b) => dist(a) - dist(b)).slice(0, 2);
  res.right = res.right.sort((a, b) => dist(a) - dist(b)).slice(0, 2);
  return res;
}

/**
 * Positions right before and after the neighbours of the click,
 * starting with the one that was picked by the click.
 * Positions within words or syntax like placeholders and tags are skipped.
 */
function getCandidates(
  view: EditorView,
  click: Click,
  { left, right }: Neighbours,
): number[] {
  const { doc } = view.state;
  const res = new Set([click.pos]);
  for (const { pos: n } of [...left, ...right]) {
    res.add(n).add(n + 1);
    forEachIsolate(view, n, (from, to, deco) => {
      if (!deco.spec.syntax && from <= n && n < to) {
        res.add(from).add(to);
      }
    });
  }
  return Array.from(res).filter(
    (pos) =>
      pos === click.pos ||
      (!(
        wordChar.test(doc.sliceString(pos - 1, pos)) &&
        wordChar.test(doc.sliceString(pos, pos + 1))
      ) &&
        !isInSyntax(view, pos)),
  );
}

const wordChar = /[\p{L}\p{N}]/u;

function forEachIsolate(
  view: EditorView,
  pos: number,
  f: (from: number, to: number, deco: Decoration) => void,
) {
  for (const source of view.state.facet(EditorView.bidiIsolatedRanges)) {
    const set = typeof source === 'function' ? source(view) : source;
    set.between(pos, pos, f);
  }
}

/**
 * Is `pos` within a placeholder or tag, and not within a quoted literal in it?
 * The ends of a literal count as within it.
 */
function isInSyntax(view: EditorView, pos: number) {
  let syntax = false;
  let size = Infinity;
  forEachIsolate(view, pos, (from, to, deco) => {
    const inside = deco.spec.syntax
      ? from < pos && pos < to
      : from <= pos && pos <= to;
    if (inside && to - from < size) {
      syntax = !!deco.spec.syntax;
      size = to - from;
    }
  });
  return syntax;
}

/**
 * After inserting `length` characters at `pos`, how far they are displayed
 * from the click. Inserted text shifts the content on one side of it, so this
 * is measured relative to the nearest neighbour of the click that moved least.
 * Moving further than the width of the inserted text means that the content
 * was reordered, which is penalised.
 */
function distanceFromClick(
  view: EditorView,
  click: Click,
  { left, right }: Neighbours,
  pos: number,
  length: number,
) {
  let tLeft = Infinity;
  let tRight = -Infinity;
  let y = click.y;
  for (let i = pos; i < pos + length; ++i) {
    const rect = view.coordsForChar(i);
    if (rect) {
      tLeft = Math.min(tLeft, rect.left);
      tRight = Math.max(tRight, rect.right);
      y = (rect.top + rect.bottom) / 2;
    }
  }
  if (tLeft > tRight) {
    return Infinity;
  }
  const shifts: number[] = [];
  for (const n of [...left, ...right]) {
    const rect = charRect(view, n.pos >= pos ? n.pos + length : n.pos, y);
    if (!rect) {
      return Infinity;
    }
    shifts.push(rect.left - n.rect.left);
  }
  const width = tRight - tLeft;
  const shift = shifts.reduce((a, b) => (Math.abs(b) < Math.abs(a) ? b : a));
  const x = click.x + shift;
  const gap = x < tLeft ? tLeft - x : x > tRight ? x - tRight : 0;

  // Neighbours on either side of the inserted text may only move apart
  // by its width; anything more means that the content was reordered.
  const spread = Math.max(...shifts) - Math.min(...shifts);
  const reordered = Math.max(0, spread - width - 1);
  return gap + reordered;
}

/** The displayed rectangle of the character at `pos`, if it's on the line at `y` */
function charRect(view: EditorView, pos: number, y: number) {
  const rect = view.coordsForChar(pos);
  return rect && rect.right > rect.left && rect.top <= y && rect.bottom >= y
    ? rect
    : null;
}
