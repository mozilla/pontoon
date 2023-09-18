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

/** Use content-based automatic direction for values inside quotes */
const dirAuto = Decoration.mark({ attributes: { dir: 'auto' } });

/** Explicitly mark placeholders and tags as LTR spans, for bidirectional contexts */
const dirLTR = Decoration.mark({
  attributes: { dir: 'ltr' },
  bidiIsolate: Direction.LTR,
});

/** Enable spellchecking only for string content, and not highlighted syntax or quoted literals */
const spellcheck = Decoration.mark({ attributes: { spellcheck: 'true' } });

/**
 * Because decorators may be nested, they need to be tracked separately
 * so that we can assign appropriate precedences to them later.
 * In the worst case, we'll have a dir=LTR tag in a dir=RTL message
 * containing a dir=auto quoted literal with a dir=LTR placeholder.
 * Because placeholders may also contain quoted literals,
 * the placeholders inside & outside literals need different precedence.
 * Luckily no format we cares about allows for
 * placeholders within quoted literals within placeholders.
 */
const getDecorations = (view: EditorView) => {
  const phIn = new RangeSetBuilder<Decoration>(); // placeholders inside quotes
  const lit = new RangeSetBuilder<Decoration>(); // quoted literals
  const phOut = new RangeSetBuilder<Decoration>(); // placeholders outside quotes
  const ts = new RangeSetBuilder<Decoration>(); // tags and spellcheck
  let ph = phOut;
  let quoteStart = -1;
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
          break;
        case 'brace':
          if (phStart === -1) {
            phStart = node.from;
          } else {
            ph.add(phStart, node.to, dirLTR);
            phStart = -1;
          }
          break;
        case 'quote':
          if (quoteStart === -1) {
            ph = phIn;
            quoteStart = node.to;
          } else {
            if (node.from > quoteStart) {
              lit.add(quoteStart, node.from, dirAuto);
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
  }
  if (quoteStart !== -1 && end > quoteStart) {
    lit.add(quoteStart, end, dirAuto);
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
        this.decorations = getDecorations(update.view);
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
