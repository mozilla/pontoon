import { syntaxTree } from '@codemirror/language';
import { Range } from '@codemirror/state';
import {
  Decoration,
  DecorationSet,
  EditorView,
  ViewPlugin,
  ViewUpdate,
} from '@codemirror/view';

/** Use content-based automatic direction for values inside quotes */
const dirAuto = Decoration.mark({ attributes: { dir: 'auto' } });

/** Explicitly mark placeholders and tags as LTR spans, for bidirectional contexts */
const dirLTR = Decoration.mark({ attributes: { dir: 'ltr' } });

/** Enable spellchecking only for string content, and not highlighted syntax or quoted literals */
const spellcheck = Decoration.mark({ attributes: { spellcheck: 'true' } });

function getTagsAndSpellcheck(view: EditorView) {
  const deco: Range<Decoration>[] = [];

  let tagStart = -1;
  let end = -1;
  syntaxTree(view.state).iterate({
    enter(node) {
      switch (node.name) {
        case 'Document':
          end = node.to;
          break;
        case 'string':
          deco.push(spellcheck.range(node.from, node.to));
          break;
        case 'bracket':
          if (tagStart === -1) {
            tagStart = node.from;
          } else {
            deco.push(dirLTR.range(tagStart, node.to));
            tagStart = -1;
          }
          break;
      }
    },
  });
  if (tagStart !== -1 && end > tagStart) {
    deco.push(dirLTR.range(tagStart, end));
  }
  return Decoration.set(deco);
}

const getPlaceholders = (initQuoted: boolean) => (view: EditorView) => {
  const deco: Range<Decoration>[] = [];

  let quoted = initQuoted;
  let phStart = -1;
  let end = -1;
  syntaxTree(view.state).iterate({
    enter(node) {
      switch (node.name) {
        case 'Document':
          end = node.to;
          break;
        case 'keyword':
          deco.push(dirLTR.range(node.from, node.to));
          break;
        case 'brace':
          if (!quoted) {
            if (phStart === -1) {
              phStart = node.from;
            } else {
              deco.push(dirLTR.range(phStart, node.to));
              phStart = -1;
            }
          }
          break;
        case 'quote':
          quoted = !quoted;
          break;
      }
    },
  });
  if (phStart !== -1 && end > phStart) {
    deco.push(dirLTR.range(phStart, end));
  }
  return Decoration.set(deco);
};

function getLiterals(view: EditorView) {
  const deco: Range<Decoration>[] = [];
  let quoted = -1;
  let end = -1;
  syntaxTree(view.state).iterate({
    enter(node) {
      if (node.to > end) {
        end = node.to;
      }
      if (node.name === 'quote') {
        if (quoted === -1) {
          quoted = node.to;
        } else {
          if (node.from > quoted) {
            deco.push(dirAuto.range(quoted, node.from));
          }
          quoted = -1;
        }
      }
    },
  });
  if (quoted !== -1 && end > quoted) {
    deco.push(dirAuto.range(quoted, end));
  }
  return Decoration.set(deco, true);
}

export const decoratorPlugins = [
  getPlaceholders(true),
  getLiterals,
  getPlaceholders(false),
  getTagsAndSpellcheck,
].map((getDecorations) =>
  ViewPlugin.fromClass(
    class {
      decorations: DecorationSet;

      constructor(view: EditorView) {
        this.decorations = getDecorations(view);
      }

      update(update: ViewUpdate) {
        if (update.docChanged) {
          this.decorations = getDecorations(update.view);
        }
      }
    },
    { decorations: (v) => v.decorations },
  ),
);
