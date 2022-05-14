/* eslint-env node */

import { createMemoryHistory } from 'history';

import { createReduxStore, mountComponentWithStore } from '~/test/store';

import { EntityDetails } from './EntityDetails';

const ENTITIES = [
  {
    pk: 42,
    original: 'le test',
    translation: [{ string: 'test', errors: [], warnings: [] }],
    project: { contact: '' },
    comment: '',
  },
];

function mockEntityDetails(pk) {
  const history = createMemoryHistory({
    initialEntries: [`/kg/pro/all/?string=${pk}`],
  });

  const initialState = {
    entities: { entities: ENTITIES },
    history: { translations: [] },
    otherlocales: { translations: [] },
    user: { settings: { forceSuggestions: true }, username: 'Franck' },
  };
  const store = createReduxStore(initialState);
  return mountComponentWithStore(EntityDetails, store, {}, history);
}

describe('<EntityDetails>', () => {
  beforeAll(() => {
    global.fetch = () =>
      Promise.resolve({
        json: () => Promise.resolve({}),
      });
  });

  afterAll(() => {
    delete global.fetch;
  });

  it('shows an empty section when no entity is selected', () => {
    const wrapper = mockEntityDetails('');
    expect(wrapper.text()).toBe('');
  });

  it('loads the correct list of components', () => {
    const wrapper = mockEntityDetails(42);

    expect(wrapper.find('.entity-navigation')).toHaveLength(1);
    expect(wrapper.find('.metadata')).toHaveLength(1);
    expect(wrapper.find('.editor')).toHaveLength(1);
    expect(wrapper.find('Helpers')).toHaveLength(1);
  });
});
