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
    key: 'key',
    original: 'Hello',
    translation: [{ string }],
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
          <EntityView.Provider value={{ entity, pluralForm: 0 }}>
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

  return [wrapper, actions, () => result];
}

describe('<TranslationForm> with one field', () => {
  it('renders a textarea with some content', () => {
    const [wrapper] = mountForm('Salut');

    expect(wrapper.find('textarea').prop('defaultValue')).toBe('Salut');
  });

  it('calls the updateTranslation function on change', () => {
    const [wrapper, _, getResult] = mountForm('hello');
    const onChange = wrapper.find('textarea').prop('onChange');
    act(() => onChange({ currentTarget: { value: 'good bye' } }));
    wrapper.update();

    expect(getResult()[0].value).toBe('good bye');
  });

  it('updates the translation when setEditorSelection is passed without focus', async () => {
    const [wrapper, actions, getResult] = mountForm('Foo');
    act(() => actions.setEditorSelection(', Bar'));
    wrapper.update();

    expect(getResult()[0].value).toBe('Foo, Bar');
  });

  it('updates the translation when setEditorSelection is passed with focus', async () => {
    const [wrapper, actions, getResult] = mountForm('Hello');
    act(() => {
      const ta = wrapper.find('textarea');
      ta.simulate('focus');
      ta.getDOMNode().setSelectionRange(5, 5);
      actions.setEditorSelection(', World');
    });
    wrapper.update();

    expect(getResult()[0].value).toBe('Hello, World');
  });
});
