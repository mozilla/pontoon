import { mount } from 'enzyme';
import { createMemoryHistory } from 'history';
import React from 'react';
import { act } from 'react-dom/test-utils';
import { Provider } from 'react-redux';

import { LocationProvider } from '~/context/location';
import * as editor from '~/core/editor';
import * as entities from '~/core/entities';
import * as plural from '~/core/plural';

import { createDefaultUser, createReduxStore } from '~/test/store';

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

function selectPlural(store, pluralForm) {
  store.dispatch(plural.actions.select(pluralForm));
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
        <GenericEditor />
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

  it('updates translation when entity or plural change', () => {
    const [wrapper, store, history] = createComponent(1);

    selectEntity(store, history, 2);
    expect(store.getState().editor.translation).toEqual('deuxième');

    selectPlural(store, 1);
    wrapper.setProps({});
    expect(store.getState().editor.translation).toEqual('deuxièmes');
  });

  it('sets initial translation when entity or plural change', () => {
    const [wrapper, store, history] = createComponent(1);

    selectEntity(store, history, 2);
    expect(store.getState().editor.initialTranslation).toEqual('deuxième');

    selectPlural(store, 1);
    wrapper.setProps({});
    expect(store.getState().editor.initialTranslation).toEqual('deuxièmes');
  });

  it('does not set initial translation when translation changes', () => {
    const [, store] = createComponent(1);
    expect(store.getState().editor.initialTranslation).toEqual('quelque chose');

    store.dispatch(editor.actions.update('autre chose'));
    expect(store.getState().editor.initialTranslation).toEqual('quelque chose');
  });
});
