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
  syntaxHighlighting,
} from '@codemirror/language';
import { Extension } from '@codemirror/state';
import { EditorView, keymap } from '@codemirror/view';
import { tags } from '@lezer/highlight';
import { useContext, useEffect, useRef } from 'react';

import { EditorActions } from '~/context/Editor';
import { useCopyOriginalIntoEditor } from '~/modules/editor';
import { decoratorPlugin } from './decoratorPlugin';
import {
  useHandleCtrlShiftArrow,
  useHandleEnter,
  useHandleEscape,
} from './editFieldShortcuts';
import { fluentMode, commonMode } from './editFieldModes';

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
    tag: [tags.bracket, tags.tagName],
    color: '#3e9682',
    fontFamily: 'monospace',
    whiteSpace: 'pre',
  }, // <...>
  { tag: tags.brace, color: '#872bff', fontWeight: 'bold', whiteSpace: 'pre' }, // { }
  { tag: tags.name, color: '#872bff', whiteSpace: 'pre' }, // {...}
  { tag: [tags.quote, tags.literal], whiteSpace: 'pre-wrap' }, // "..."
  { tag: tags.string, whiteSpace: 'pre-wrap' },
]);

export const getExtensions = (
  format: string,
  ref: ReturnType<typeof useKeyHandlers>,
): Extension[] => [
  history(),
  closeBrackets(),
  EditorView.lineWrapping,
  StreamLanguage.define<any>(format === 'fluent' ? fluentMode : commonMode),
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
