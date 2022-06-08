/* eslint-env node */

import { createMemoryHistory } from 'history';
import React from 'react';

import { EntityView } from '~/context/EntityView';
import { createReduxStore, mountComponentWithStore } from '~/test/store';

import { EntityDetails } from './EntityDetails';

const ENTITY = {
  pk: 42,
  original: 'le test',
  translation: [{ string: 'test', errors: [], warnings: [] }],
  project: { contact: '' },
  comment: '',
};

function mockEntityDetails(pk) {
  const history = createMemoryHistory({
    initialEntries: [`/kg/pro/all/?string=${pk}`],
  });

  const initialState = {
    otherlocales: { translations: [] },
    user: { settings: { forceSuggestions: true }, username: 'Franck' },
  };
  const store = createReduxStore(initialState);
  const Component = () => (
    <EntityView.Provider
      value={{
        entity: ENTITY,
        hasPluralForms: false,
        pluralForm: 0,
        setPluralForm: () => {},
      }}
    >
      <EntityDetails />
    </EntityView.Provider>
  );
  return mountComponentWithStore(Component, store, {}, history);
}

describe('<EntityDetails>', () => {
  beforeAll(() => {
    global.fetch = () => Promise.resolve({ json: () => Promise.resolve({}) });
  });

  afterAll(() => {
    delete global.fetch;
  });

  it('loads the correct list of components', () => {
    const wrapper = mockEntityDetails(42);

    expect(wrapper.find('.entity-navigation')).toHaveLength(1);
    expect(wrapper.find('.metadata')).toHaveLength(1);
    expect(wrapper.find('.editor')).toHaveLength(1);
    expect(wrapper.find('Helpers')).toHaveLength(1);
  });
});
