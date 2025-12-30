import React from 'react';

import { HistoryData } from '~/context/HistoryData';
import { createReduxStore, mountComponentWithStore } from '~/test/store';

import { History } from './History';
import { vi } from 'vitest';

vi.mock('react-time-ago', () => {
  return {
    default: () => null,
  };
});

function mountHistory(fetching, translations) {
  const store = createReduxStore({
    entities: { entities: [{ pk: 0, original: 'exists' }] },
    user: {},
  });
  return mountComponentWithStore(
    () => (
      <HistoryData.Provider value={{ fetching, translations }}>
        <History />
      </HistoryData.Provider>
    ),
    store,
  );
}

describe('<History>', () => {
  it('shows the correct number of translations', () => {
    const wrapper = mountHistory(false, [
      { pk: 1, userBanner: '' },
      { pk: 2, userBanner: '' },
      { pk: 3, userBanner: '' },
    ]);

    expect(wrapper.find('ul > *')).toHaveLength(3);
  });

  it('returns null while history is loading', () => {
    const wrapper = mountHistory(true, []);

    expect(wrapper.find('HistoryTranslationComponent > *')).toHaveLength(0);
  });

  it('renders a no results message if history is empty', () => {
    const wrapper = mountHistory(false, []);

    expect(wrapper.find('#history-History--no-translations')).toHaveLength(1);
  });
});
