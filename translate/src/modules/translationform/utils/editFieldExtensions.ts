import {
  acceptCompletion,
  autocompletion,
  closeBrackets,
  closeBracketsKeymap,
  type CompletionSource,
} from '@codemirror/autocomplete';
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
import { EditorView, keymap, tooltips } from '@codemirror/view';
import { tags } from '@lezer/highlight';
import { useContext, useEffect, useRef } from 'react';

import { EditorActions } from '~/context/Editor';
import { useCopyOriginalIntoEditor } from '~/modules/editor';
import { placeholder } from '~/modules/placeable/placeholder';
import { MessageEntry, parseEntry } from '~/utils/message';
import { editablePattern } from '~/utils/message/placeholders';
import { decoratorPlugin } from './decoratorPlugin';
import {
  useHandleCtrlShiftArrow,
  useHandleEnter,
  useHandleEscape,
} from './editFieldShortcuts';
import { fluentMode, commonMode, webextMode } from './editFieldModes';
import { Message } from '@mozilla/l10n';

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
  orig: string,
  ref: ReturnType<typeof useKeyHandlers>,
): Extension[] => [
  history(),
  // .main-column sets overflow-y:auto, which disables overflow-x:visible,
  // and so an absolute-positioned tooltip in the .editor would introduce
  // horizontal scrolling if it overflows the right edge of .main-column.
  // We avoid this by placing tooltips in its parent container.
  tooltips({ parent: document.querySelector('.panel-content') as HTMLElement }),
  autocompletePlaceholders(format, orig) ?? closeBrackets(),
  EditorView.lineWrapping,
  StreamLanguage.define<any>(
    format === 'fluent'
      ? fluentMode
      : format === 'webext'
        ? webextMode
        : commonMode,
  ),
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
    { key: 'Tab', run: acceptCompletion },
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

/**
 * Autocomplete placeholders, and sequences of placeholders.
 *
 * For a source like
 *
 *     <foo>{$bar}</foo> baz
 *
 * generates completions for:
 * - `<foo>`
 * - `<foo>{$bar}`
 * - `<foo>{$bar}</foo>`
 * - `{$bar}`
 * - `{$bar}</foo>`
 * - `</foo>`
 *
 * If no autocompletions are found, bracket auto-closing is enabled.
 */
function autocompletePlaceholders(format: string, source: string) {
  const override: CompletionSource[] = [];
  for (const pattern of entryPatterns(format, source)) {
    const highlights: [start: number, ends: number[]][] = [];
    for (const match of pattern.matchAll(placeholder)) {
      const label = match[0].trimEnd();
      if (label.length > 1) {
        const start = match.index;
        const end = start + label.length;
        for (const hl of highlights) {
          if (hl[1].includes(start)) hl[1].push(end);
        }
        highlights.push([start, [end]]);
      }
    }
    for (const hl of highlights) {
      override.push(completePlaceholder(pattern, ...hl));
    }
  }
  return override.length ? autocompletion({ override }) : null;
}

function* entryPatterns(format: string, source: string) {
  const entry = parseEntry(format, source);
  if (entry) {
    if (entry.value) yield* msgPatterns(entry.format, entry.value);
    if (entry.attributes) {
      for (const msg of entry.attributes.values()) {
        yield* msgPatterns(entry.format, msg);
      }
    }
  }
}

function* msgPatterns(format: MessageEntry['format'], msg: Message) {
  if (Array.isArray(msg)) yield editablePattern(msg);
  else if (msg.msg) yield editablePattern(msg.msg);
  else for (const v of msg.alt) yield editablePattern(v.pat);
}

function completePlaceholder(
  orig: string,
  start: number,
  ends: number[],
): CompletionSource {
  const esc = (chars: string) => chars.replace(/[^\w\s]/g, '\\$&');
  const rest = new Set(orig.substring(start + 1, ends[0]));
  const restChars = Array.from(rest).join('');
  const match = new RegExp(`[${esc(orig[start])}][${esc(restChars)}]*$`);
  // Deprioritize closing tags, as they otherwise show up first in the list.
  const boost = orig.substring(start, start + 2) === '</' ? -1 : 0;
  const options = ends.map((end) => ({
    label: orig.substring(start, end),
    boost,
  }));
  return (context) => {
    const token = context.matchBefore(match);
    if (token) return { from: token.from, options };
    else return context.explicit ? { from: context.pos, options } : null;
  };
}
