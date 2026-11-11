import {
  ensureSyntaxTree,
  type StreamLanguage,
  syntaxTree,
} from '@codemirror/language';
import { EditorState } from '@codemirror/state';

import {
  commonLanguageMode,
  fluentLanguageMode,
  webextLanguageMode,
} from './editFieldModes';

const LONG_DOC = `<a ${'x '.repeat(300)}\n${'y '.repeat(30)}>`;

function fullyParsed(mode: StreamLanguage<any>, doc: string): EditorState {
  const state = EditorState.create({
    doc,
    extensions: [mode],
  });
  ensureSyntaxTree(state, state.doc.length, 5000);
  return state;
}

describe.each([
  ['fluent', fluentLanguageMode],
  ['common', commonLanguageMode],
  ['webext', webextLanguageMode],
])('%s mode', (_name, mode: StreamLanguage<any>) => {
  test('applies an edit resuming from a parser state snapshot (#4438)', () => {
    let state = fullyParsed(mode, LONG_DOC);
    state = state.update({
      changes: { from: state.doc.length, insert: 'X' },
    }).state;
    ensureSyntaxTree(state, state.doc.length, 5000);

    expect(state.doc.toString()).toBe(`${LONG_DOC}X`);
    expect(syntaxTree(state).toString()).toBe(
      syntaxTree(fullyParsed(mode, `${LONG_DOC}X`)).toString(),
    );
  });
});
