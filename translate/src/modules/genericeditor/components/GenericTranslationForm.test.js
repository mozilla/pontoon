import React, { useContext } from 'react';
import { act } from 'react-dom/test-utils';

import { EditorActions, EditorProvider } from '~/context/Editor';
import { EntityView } from '~/context/EntityView';
import { Locale } from '~/context/Locale';

import {
  createDefaultUser,
  createReduxStore,
  mountComponentWithStore,
} from '~/test/store';
import { MockLocalizationProvider } from '~/test/utils';

import { GenericTranslationForm } from './GenericTranslationForm';

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
    original: 'Hello',
    translation: [{ string }],
  };

  let actions;
  const Spy = () => {
    actions = useContext(EditorActions);
    return null;
  };

  const wrapper = mountComponentWithStore(
    () => (
      <Locale.Provider value={DEFAULT_LOCALE}>
        <MockLocalizationProvider>
          <EntityView.Provider value={{ entity, pluralForm: 0 }}>
            <EditorProvider>
              <Spy />
              <GenericTranslationForm />
            </EditorProvider>
          </EntityView.Provider>
        </MockLocalizationProvider>
      </Locale.Provider>
    ),
    store,
  );

  return [wrapper, actions];
}

describe('<GenericTranslationForm>', () => {
  it('renders a textarea with some content', () => {
    const [wrapper] = mountForm('Salut');

    expect(wrapper.find('textarea').prop('value')).toBe('Salut');
  });

  it('calls the updateTranslation function on change', () => {
    const [wrapper] = mountForm('hello');
    const onChange = wrapper.find('textarea').prop('onChange');
    act(() => onChange({ currentTarget: { value: 'good bye' } }));
    wrapper.update();

    expect(wrapper.find('textarea').prop('value')).toBe('good bye');
  });

  it('updates the translation when setEditorSelection is passed', async () => {
    const [wrapper, actions] = mountForm('Hello');
    act(() => actions.setEditorSelection('World, '));
    wrapper.update();

    expect(wrapper.find('textarea').prop('value')).toBe('World, Hello');
  });
});
