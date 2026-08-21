import { EditorView } from '@codemirror/view';
import React, { useContext } from 'react';
import { act } from 'react-dom/test-utils';

import { EditorActions, EditorProvider, EditorResult } from '~/context/Editor';
import { EntityView } from '~/context/EntityView';
import { Locale } from '~/context/Locale';

import {
  createDefaultUser,
  createReduxStore,
  mountComponentWithStore,
} from '~/test/store';
import { MockLocalizationProvider } from '~/test/utils';

import { TranslationForm } from './TranslationForm';

const DEFAULT_LOCALE = {
  direction: 'ltr',
  code: 'kg',
  script: 'Latn',
  cldrPlurals: [1, 5],
};

function mountForm(string) {
  const store = createReduxStore();
  createDefaultUser(store);

  const entity = {
    pk: 0,
    key: ['key'],
    original: 'Hello',
    value: ['Hello'],
    translation: { string, value: [string] },
  };

  let actions, result;
  const Spy = () => {
    actions = useContext(EditorActions);
    result = useContext(EditorResult);
    return null;
  };

  const { container } = mountComponentWithStore(
    () => (
      <Locale.Provider value={DEFAULT_LOCALE}>
        <MockLocalizationProvider>
          <EntityView.Provider value={{ entity }}>
            <EditorProvider>
              <Spy />
              <TranslationForm />
            </EditorProvider>
          </EntityView.Provider>
        </MockLocalizationProvider>
      </Locale.Provider>
    ),
    store,
  );

  const view = EditorView.findFromDOM(
    container.querySelector('.singlefield .cm-content'),
  );

  return { actions, getResult: () => result, view };
}

describe('<TranslationForm> with one field', () => {
  it('renders an editor with some content', () => {
    const { view } = mountForm('Salut');
    expect(view.state.doc.toString()).toBe('Salut');
  });

  it('updates the result on change', () => {
    const { view, getResult } = mountForm('hello');
    act(() =>
      view.dispatch({
        changes: { from: 0, to: view.state.doc.length, insert: 'good bye' },
      }),
    );
    expect(getResult()).toEqual({
      format: 'plain',
      id: 'key',
      value: ['good bye'],
    });
  });

  it('updates the translation when setEditorSelection is passed without focus', async () => {
    const { actions, getResult } = mountForm('Foo');
    act(() => actions.setEditorSelection(', Bar'));

    expect(getResult()).toEqual({
      format: 'plain',
      id: 'key',
      value: ['Foo, Bar'],
    });
  });

  it('draws the caret only while the field is empty', () => {
    // drawSelection fixes tiny native caret (#4249) but regresses RTL selection (#4240)
    // hence emptyEditorCaret toggles it on the empty <-> content boundary
    // Not needed after https://bugzilla.mozilla.org/show_bug.cgi?id=2056439 is fixed
    const { view } = mountForm('');
    const hasDrawnCaret = () => !!view.dom.querySelector('.cm-cursorLayer');

    expect(hasDrawnCaret()).toBe(true);

    act(() => view.dispatch({ changes: { from: 0, insert: 'test' } }));
    expect(hasDrawnCaret()).toBe(false);

    act(() =>
      view.dispatch({
        changes: { from: 0, to: view.state.doc.length, insert: '' },
      }),
    );
    expect(hasDrawnCaret()).toBe(true);
  });

  it('updates the translation when setEditorSelection is passed with focus', async () => {
    const { actions, getResult, view } = mountForm('Hello');
    act(() => {
      view.focus();
      view.dispatch({ selection: { anchor: view.state.doc.length } });
      actions.setEditorSelection(', World');
    });

    expect(getResult()).toEqual({
      format: 'plain',
      id: 'key',
      value: ['Hello, World'],
    });
  });
});
