import { syntaxTree } from '@codemirror/language';
import { Prec, RangeSetBuilder } from '@codemirror/state';
import {
  Decoration,
  DecorationSet,
  Direction,
  EditorView,
  ViewPlugin,
  ViewUpdate,
} from '@codemirror/view';
import type { Tree } from '@lezer/common';

/**
 * Values inside quotes may be either LTR or RTL, so their direction is detected
 * from their content. This is set explicitly rather than with `dir="auto"`,
 * so that the browser and CodeMirror's cursor motion agree on it.
 */
const literalDir = {
  [Direction.LTR]: Decoration.mark({
    attributes: { dir: 'ltr' },
    bidiIsolate: Direction.LTR,
  }),
  [Direction.RTL]: Decoration.mark({
    attributes: { dir: 'rtl' },
    bidiIsolate: Direction.RTL,
  }),
};

const rtlChar =
  /[\u0590-\u08FF\uFB1D-\uFDFF\uFE70-\uFEFC\u{10800}-\u{10FFF}\u{1E800}-\u{1EFFF}]/u;
const ltrChar = /\p{L}/u;
const rtlCharGlobal = new RegExp(rtlChar.source, 'gu');

/**
 * A literal is shown in the editor's direction if it contains any text in that
 * direction, and otherwise in the opposite direction if it contains any text
 * in that, skipping any placeholders, which are isolated as LTR.
 * Literals are always in an LTR context, so default to that.
 *
 * Unlike the first-strong rule of `dir="auto"`, this does not flip
 * the direction of the whole literal when typing at its start.
 */
function getLiteralDirection(
  view: EditorView,
  from: number,
  to: number,
  placeholders: Array<[number, number]>,
) {
  let hasRtl = false;
  let hasLtr = false;
  let pos = from;
  for (const [phFrom, phTo] of [...placeholders, [to, to]]) {
    const text = view.state.sliceDoc(pos, Math.min(phFrom, to));
    hasRtl ||= rtlChar.test(text);
    hasLtr ||= ltrChar.test(text.replace(rtlCharGlobal, ''));
    pos = Math.max(pos, phTo);
  }
  if (view.textDirection === Direction.RTL) {
    return hasRtl ? Direction.RTL : Direction.LTR;
  }
  return hasRtl && !hasLtr ? Direction.RTL : Direction.LTR;
}

/** Explicitly mark placeholders and tags as LTR spans, for bidirectional contexts */
const dirLTR = Decoration.mark({
  attributes: { dir: 'ltr' },
  bidiIsolate: Direction.LTR,
  /** Used by `bidiTyping` */
  syntax: true,
});

/** Enable spellchecking only for string content, and not highlighted syntax or quoted literals */
const spellcheck = Decoration.mark({ attributes: { spellcheck: 'true' } });

/**
 * Because decorators may be nested, they need to be tracked separately
 * so that we can assign appropriate precedences to them later.
 * In the worst case, we'll have a dir=LTR tag in a dir=RTL message
 * containing a dir=RTL quoted literal with a dir=LTR placeholder.
 * Because placeholders may also contain quoted literals,
 * the placeholders inside & outside literals need different precedence.
 * Luckily no format we cares about allows for
 * placeholders within quoted literals within placeholders.
 */
const getDecorations = (view: EditorView, prevLiterals?: DecorationSet) => {
  const phIn = new RangeSetBuilder<Decoration>(); // placeholders inside quotes
  const lit = new RangeSetBuilder<Decoration>(); // quoted literals
  const phOut = new RangeSetBuilder<Decoration>(); // placeholders outside quotes
  const ts = new RangeSetBuilder<Decoration>(); // tags and spellcheck
  // Keep the direction of literals that are being edited,
  // so that it does not flip while typing.
  const addLiteral = (
    from: number,
    to: number,
    placeholders: Array<[number, number]>,
  ) => {
    let dir: Direction | null = null;
    prevLiterals?.between(from, to, (pFrom, pTo, deco) => {
      if (pFrom < to && pTo > from) {
        dir = deco.spec.bidiIsolate;
        return false;
      }
    });
    dir ??= getLiteralDirection(view, from, to, placeholders);
    lit.add(from, to, literalDir[dir]);
  };

  let ph = phOut;
  let quoteStart = -1;
  let litPlaceholders: Array<[number, number]> = [];
  let phStart = -1;
  let tagStart = -1;
  let end = -1;
  syntaxTree(view.state).iterate({
    enter(node) {
      switch (node.name) {
        case 'Document':
          end = node.to;
          break;
        case 'keyword':
          ph.add(node.from, node.to, dirLTR);
          if (quoteStart !== -1) {
            litPlaceholders.push([node.from, node.to]);
          }
          break;
        case 'brace':
          if (phStart === -1) {
            phStart = node.from;
          } else {
            ph.add(phStart, node.to, dirLTR);
            if (quoteStart !== -1) {
              litPlaceholders.push([phStart, node.to]);
            }
            phStart = -1;
          }
          break;
        case 'quote':
          if (quoteStart === -1) {
            ph = phIn;
            quoteStart = node.to;
            litPlaceholders = [];
          } else {
            if (node.from > quoteStart) {
              addLiteral(quoteStart, node.from, litPlaceholders);
            }
            ph = phOut;
            quoteStart = -1;
          }
          break;
        case 'string':
          ts.add(node.from, node.to, spellcheck);
          break;
        case 'bracket':
          if (tagStart === -1) {
            tagStart = node.from;
          } else {
            ts.add(tagStart, node.to, dirLTR);
            tagStart = -1;
          }
          break;
      }
    },
  });
  if (phStart !== -1 && end > phStart) {
    ph.add(phStart, end, dirLTR);
    if (quoteStart !== -1) {
      litPlaceholders.push([phStart, end]);
    }
  }
  if (quoteStart !== -1 && end > quoteStart) {
    addLiteral(quoteStart, end, litPlaceholders);
  }
  if (tagStart !== -1 && end > tagStart) {
    ts.add(tagStart, end, dirLTR);
  }
  return {
    literals: lit.finish(),
    placeholdersOutsideQuotes: phOut.finish(),
    placeholdersInsideQuotes: phIn.finish(),
    tagsAndSpellcheck: ts.finish(),
  };
};

export const decoratorPlugin = ViewPlugin.fromClass(
  class {
    decorations: ReturnType<typeof getDecorations>;
    tree: Tree;
    constructor(view: EditorView) {
      this.decorations = getDecorations(view);
      this.tree = syntaxTree(view.state);
    }
    update(update: ViewUpdate) {
      if (update.docChanged || syntaxTree(update.state) != this.tree) {
        const { literals } = this.decorations;
        this.decorations = getDecorations(
          update.view,
          update.docChanged ? literals.map(update.changes) : literals,
        );
        this.tree = syntaxTree(update.state);
      }
    }
  },
  {
    provide(plugin) {
      const list = (
        get: (deco: ReturnType<typeof getDecorations>) => DecorationSet,
      ) => {
        const get_ = (view: EditorView) => {
          const pi = view.plugin(plugin);
          return pi ? get(pi.decorations) : Decoration.none;
        };
        return [
          EditorView.decorations.of(get_),
          EditorView.bidiIsolatedRanges.of(get_),
        ];
      };
      return [
        Prec.high(list((deco) => deco.placeholdersInsideQuotes)),
        Prec.default(list((deco) => deco.literals)),
        Prec.low(list((deco) => deco.placeholdersOutsideQuotes)),
        Prec.lowest(list((deco) => deco.tagsAndSpellcheck)),
      ];
    },
  },
);
