/* eslint-env node */
/* global global */

import { createMemoryHistory } from 'history';
import React from 'react';

import { EntityView } from '~/context/EntityView';
import { createReduxStore, mountComponentWithStore } from '~/test/store';

import { EntityDetails } from './EntityDetails';

const ENTITY = (pk) => ({
  pk,
  key: [],
  original: 'le test',
  translation: { string: 'test', errors: [], warnings: [] },
  project: { contact: '' },
  comment: '',
  meta: [],
  date_created: new Date().toISOString(),
});

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
    <EntityView.Provider value={{ entity: ENTITY(pk) }}>
      <EntityDetails />
    </EntityView.Provider>
  );
  return mountComponentWithStore(Component, store, {}, history);
}

describe('<EntityDetails>', () => {
  let urls = [];
  beforeAll(() => {
    global.fetch = (url) => {
      urls.push(url);
      return Promise.resolve({ json: () => Promise.resolve({}) });
    };
  });

  afterAll(() => {
    delete global.fetch;
  });

  it('loads the correct list of components', () => {
    urls = [];
    const { container, queryByTestId } = mockEntityDetails(42);
    expect(urls).toMatchObject([
      'http://localhost/other-locales/?entity=42&locale=kg',
      'http://localhost/get-team-comments/?entity=42&locale=kg',
    ]);

    expect(container.querySelector('.entity-navigation')).toBeInTheDocument();
    expect(container.querySelector('.metadata')).toBeInTheDocument();
    expect(container.querySelector('.editor')).toBeInTheDocument();
    expect(queryByTestId('helpers')).toBeInTheDocument();
  });

  it('does not load anything for entity 0', () => {
    urls = [];
    const { container, queryByTestId } = mockEntityDetails(0);
    expect(urls).toMatchObject([]);

    expect(
      container.querySelector('.entity-navigation'),
    ).not.toBeInTheDocument();
    expect(container.querySelector('.metadata')).not.toBeInTheDocument();
    expect(container.querySelector('.editor')).not.toBeInTheDocument();
    expect(queryByTestId('helpers')).not.toBeInTheDocument();
  });
});
