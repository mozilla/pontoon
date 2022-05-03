import { mount } from 'enzyme';
import { createMemoryHistory } from 'history';
import React from 'react';
import { act } from 'react-dom/test-utils';
import { Provider } from 'react-redux';

import { Locale } from '~/context/locale';
import { LocationProvider } from '~/context/location';
import { PluralFormProvider } from '~/context/pluralForm';
import * as editor from '~/core/editor';
import * as entities from '~/core/entities';

import { createDefaultUser, createReduxStore } from '~/test/store';
import { MockLocalizationProvider } from '~/test/utils';

import GenericEditor from './GenericEditor';

const ENTITIES = [
  {
    pk: 1,
    original: 'something',
    translation: [
      {
        string: 'quelque chose',
      },
    ],
  },
  {
    pk: 2,
    original: 'second',
    original_plural: 'seconds',
    translation: [{ string: 'deuxième' }, { string: 'deuxièmes' }],
  },
];

function selectEntity(store, history, entityIndex) {
  act(() => history.push(`?string=${entityIndex}`));
  store.dispatch(editor.actions.reset());
}

function createComponent(entityIndex = 0) {
  const store = createReduxStore();
  createDefaultUser(store);

  const history = createMemoryHistory({
    initialEntries: ['/kg/firefox/all-resources/'],
  });

  const wrapper = mount(
    <Provider store={store}>
      <LocationProvider history={history}>
        <MockLocalizationProvider>
          <PluralFormProvider>
            <Locale.Provider value={{ cldrPlurals: [1, 5] }}>
              <GenericEditor />
            </Locale.Provider>
          </PluralFormProvider>
        </MockLocalizationProvider>
      </LocationProvider>
    </Provider>,
  );

  store.dispatch(entities.actions.receive(ENTITIES));
  selectEntity(store, history, entityIndex);

  // Force a re-render.
  wrapper.setProps({});

  return [wrapper, store, history];
}

describe('<Editor>', () => {
  it('updates translation on mount', () => {
    const [, store] = createComponent(1);
    expect(store.getState().editor.translation).toEqual('quelque chose');
  });

  it('sets initial translation on mount', () => {
    const [, store] = createComponent(1);
    expect(store.getState().editor.initialTranslation).toEqual('quelque chose');
  });

  it('updates translation & initialTranslation when entity or plural change', () => {
    const [wrapper, store, history] = createComponent(1);

    selectEntity(store, history, 2);
    expect(store.getState().editor).toMatchObject({
      initialTranslation: 'deuxième',
      translation: 'deuxième',
    });

    wrapper.update();
    wrapper.find('.plural-selector li:last-child button').simulate('click', {});

    expect(store.getState().editor).toMatchObject({
      initialTranslation: 'deuxièmes',
      translation: 'deuxièmes',
    });
  });

  it('does not set initial translation when translation changes', () => {
    const [, store] = createComponent(1);
    expect(store.getState().editor.initialTranslation).toEqual('quelque chose');

    store.dispatch(editor.actions.update('autre chose'));
    expect(store.getState().editor.initialTranslation).toEqual('quelque chose');
  });
});
