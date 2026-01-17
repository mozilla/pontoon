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
  script: 'Latin',
  cldrPlurals: [1, 5],
};

function mountForm(string) {
  const store = createReduxStore();
  createDefaultUser(store);

  const entity = {
    pk: 0,
    key: ['key'],
    original: 'Hello',
    translation: { string },
  };

  let actions, result;
  const Spy = () => {
    actions = useContext(EditorActions);
    result = useContext(EditorResult);
    return null;
  };

  const wrapper = mountComponentWithStore(
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

  const view = wrapper.container.querySelector('.singlefield .cm-content')
    .cmView.view;

  return { actions, getResult: () => result, view, wrapper };
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
    expect(getResult()[0].value).toBe('good bye');
  });

  it('updates the translation when setEditorSelection is passed without focus', async () => {
    const { wrapper, actions, getResult } = mountForm('Foo');
    act(() => actions.setEditorSelection(', Bar'));

    expect(getResult()[0].value).toBe('Foo, Bar');
  });

  it('updates the translation when setEditorSelection is passed with focus', async () => {
    const { actions, getResult, view, wrapper } = mountForm('Hello');
    act(() => {
      view.focus();
      view.dispatch({ selection: { anchor: view.state.doc.length } });
      actions.setEditorSelection(', World');
    });

    expect(getResult()[0].value).toBe('Hello, World');
  });
});
