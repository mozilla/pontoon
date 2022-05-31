import { createReduxStore, mountComponentWithStore } from '~/test/store';

import { History } from './History';

jest.mock('react-time-ago', () => () => null);

describe('<History>', () => {
  it('shows the correct number of translations', () => {
    const store = createReduxStore({
      entities: { entities: [{ pk: 0, original: 'exists' }] },
      history: { translations: [{ pk: 1 }, { pk: 2 }, { pk: 3 }] },
      user: {},
    });
    const wrapper = mountComponentWithStore(History, store);

    expect(wrapper.find('ul > *')).toHaveLength(3);
  });

  it('returns null while history is loading', () => {
    const store = createReduxStore({
      entities: { entities: [{ pk: 0, original: 'exists' }] },
      history: { fetching: true, translations: [] },
      user: {},
    });
    const wrapper = mountComponentWithStore(History, store);

    expect(wrapper.find('History > *')).toHaveLength(0);
  });

  it('renders a no results message if history is empty', () => {
    const store = createReduxStore({
      entities: { entities: [{ pk: 0, original: 'exists' }] },
      history: { fetching: false, translations: [] },
      user: {},
    });
    const wrapper = mountComponentWithStore(History, store);

    expect(wrapper.find('#history-History--no-translations')).toHaveLength(1);
  });
});
