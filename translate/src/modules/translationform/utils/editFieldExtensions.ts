import { closeBrackets, closeBracketsKeymap } from '@codemirror/autocomplete';
import {
  history,
  historyKeymap,
  insertNewlineAndIndent,
  standardKeymap,
} from '@codemirror/commands';
import {
  HighlightStyle,
  StreamLanguage,
  bracketMatching,
  syntaxHighlighting,
  syntaxTree,
} from '@codemirror/language';
import { Extension, Range } from '@codemirror/state';
import {
  Decoration,
  DecorationSet,
  EditorView,
  ViewPlugin,
  ViewUpdate,
  keymap,
} from '@codemirror/view';
import { useContext, useEffect, useRef } from 'react';

import { EditorActions } from '~/context/Editor';
import { useCopyOriginalIntoEditor } from '~/modules/editor';
import {
  useHandleCtrlShiftArrow,
  useHandleEnter,
  useHandleEscape,
} from './editFieldShortcuts';
import { fluentMode, commonMode } from './editFieldModes';
import { tags } from '@lezer/highlight';

/**
 * Key handlers depend on application state,
 * so rather than updating the keymap continuously,
 * let's use a ref for the handlers instead.
 */
export function useKeyHandlers() {
  const { clearEditor } = useContext(EditorActions);
  const copyOriginalIntoEditor = useCopyOriginalIntoEditor();
  const onCtrlShiftArrow = useHandleCtrlShiftArrow();
  const onEnter = useHandleEnter();
  const onEscape = useHandleEscape();

  const handlers = {
    onCtrlShiftArrow,
    onCtrlShiftBackspace() {
      clearEditor();
      return true as const;
    },
    onCtrlShiftC() {
      copyOriginalIntoEditor();
      return true as const;
    },
    onEnter,
    onEscape,
  };
  const ref = useRef(handlers);
  useEffect(() => {
    ref.current = handlers;
  });
  return ref;
}

const style = HighlightStyle.define([
  {
    tag: tags.keyword,
    color: '#872bff',
    fontFamily: 'monospace',
    whiteSpace: 'pre',
  }, // printf
  {
    tag: tags.tagName,
    color: '#3e9682',
    fontFamily: 'monospace',
    whiteSpace: 'pre',
  }, // <...>
  { tag: tags.brace, color: '#872bff', fontWeight: 'bold', whiteSpace: 'pre' }, // {...}
  { tag: tags.name, color: '#872bff', whiteSpace: 'pre' }, // {...}
]);

// Enable spellchecking only for string content, and not highlighted syntax
const spellcheckMark = Decoration.mark({ attributes: { spellcheck: 'true' } });
// Explicitly mark syntax as contiguous LTR spans, for bidirectional contexts
const directionMark = Decoration.mark({ attributes: { dir: 'ltr' } });
const decoratorPlugin = ViewPlugin.fromClass(
  class {
    decorations: DecorationSet;
    constructor(view: EditorView) {
      this.decorations = this.getDecorations(view);
    }
    update(update: ViewUpdate) {
      if (update.docChanged) {
        this.decorations = this.getDecorations(update.view);
      }
    }
    private getDecorations(view: EditorView) {
      const deco: Range<Decoration>[] = [];
      let syntax: [from: number, to: number] | null = null;
      syntaxTree(view.state).iterate({
        enter(node) {
          switch (node.name) {
            case 'string':
              if (syntax) {
                if (syntax[1] > syntax[0]) {
                  deco.push(directionMark.range(syntax[0], syntax[1]));
                }
                syntax = null;
              }
              deco.push(spellcheckMark.range(node.from, node.to));
              break;
            case 'brace':
            case 'keyword':
            case 'name':
            case 'tagName':
              syntax = [syntax?.[0] ?? node.from, node.to];
              break;
          }
        },
      });
      if (syntax && syntax[1] > syntax[0]) {
        deco.push(directionMark.range(syntax[0], syntax[1]));
      }
      return Decoration.set(deco);
    }
  },
  { decorations: (v) => v.decorations },
);

export const getExtensions = (
  format: string,
  ref: ReturnType<typeof useKeyHandlers>,
): Extension[] => [
  history(),
  bracketMatching(),
  closeBrackets(),
  EditorView.lineWrapping,
  StreamLanguage.define<any>(format === 'ftl' ? fluentMode : commonMode),
  syntaxHighlighting(style),
  decoratorPlugin,
  keymap.of([
    {
      key: 'Enter',
      run: () => ref.current.onEnter(),
      shift: insertNewlineAndIndent,
    },
    { key: 'Mod-Enter', run: insertNewlineAndIndent },
    { key: 'Escape', run: () => ref.current.onEscape() },
    {
      key: 'Shift-Ctrl-ArrowDown',
      run: () => ref.current.onCtrlShiftArrow('ArrowDown'),
    },
    {
      key: 'Shift-Ctrl-ArrowUp',
      run: () => ref.current.onCtrlShiftArrow('ArrowUp'),
    },
    {
      key: 'Shift-Ctrl-Backspace',
      run: () => ref.current.onCtrlShiftBackspace(),
    },
    { key: 'Shift-Ctrl-c', run: () => ref.current.onCtrlShiftC() },
    ...closeBracketsKeymap,
    ...standardKeymap,
    ...historyKeymap,
  ]),
];
