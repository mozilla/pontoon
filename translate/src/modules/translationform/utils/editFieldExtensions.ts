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
import { Decoration, EditorView, ViewPlugin, keymap } from '@codemirror/view';
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
  { tag: tags.keyword, color: '#872bff', fontFamily: 'monospace' }, // printf
  { tag: tags.tagName, color: '#3e9682', fontFamily: 'monospace' }, // <...>
  { tag: tags.brace, color: '#872bff', fontWeight: 'bold' }, // {...}
  { tag: tags.name, color: '#872bff' }, // {...}
]);

// Enable spellchecking only for string content, and not highlighted syntax
const spellcheckMark = Decoration.mark({ attributes: { spellcheck: 'true' } });
const spellcheckPlugin = ViewPlugin.define(
  (view) => {
    const deco: Range<Decoration>[] = [];
    syntaxTree(view.state).iterate({
      enter(node) {
        if (node.name == 'string') {
          deco.push(spellcheckMark.range(node.from, node.to));
        }
      },
    });
    // Wrap in Array to avoid update() method conflicts
    return [Decoration.set(deco)];
  },
  { decorations: (v) => v[0] },
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
  spellcheckPlugin,
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
