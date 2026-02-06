import { createMemoryHistory } from 'history';
import React from 'react';

import { Locale } from '~/context/Locale';
import { createReduxStore, mountComponentWithStore } from '~/test/store';

import { Navigation } from './Navigation';

const HISTORY = createMemoryHistory({
  initialEntries: ['/kg/mark42/stuff.ftl/'],
});

const LOCALE = {
  code: 'kg',
  name: 'Klingon',
};

const PROJECT = {
  name: 'Mark 42',
};

const NavigationWrapper = () => (
  <Locale.Provider value={LOCALE}>
    <Navigation />
  </Locale.Provider>
);

describe('<Navigation>', () => {
  it('shows navigation', () => {
    const store = createReduxStore({ project: PROJECT });
    const wrapper = mountComponentWithStore(
      NavigationWrapper,
      store,
      {},
      HISTORY,
    );

    expect(wrapper.container).toHaveTextContent('Klingon');
    expect(wrapper.container).toHaveTextContent('kg');
  });
});
