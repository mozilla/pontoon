import { createReduxStore, mountComponentWithStore } from '~/test/store';

import { ResourceProgress } from './ResourceProgress';
import { vi } from 'vitest';
import { fireEvent } from '@testing-library/react';

describe('<ResourceProgress>', () => {
  const STATS = {
    approved: 5,
    pretranslated: 4,
    unreviewed: 5,
    warnings: 3,
    errors: 2,
    missing: 1,
    total: 15,
  };
  const PARAMETERS = {
    entity: 0,
    locale: 'en-GB',
    project: 'tutorial',
    resource: 'all-resources',
    status: 'errors',
    search: null,
  };

  beforeAll(() => {
    HTMLCanvasElement.prototype.getContext = vi.fn();
  });

  it('shows only a selector by default', () => {
    const store = createReduxStore({ stats: STATS });
    const wrapper = mountComponentWithStore(ResourceProgress, store, {
      parameters: PARAMETERS,
    });

    expect(wrapper.container.querySelector('.selector')).toBeInTheDocument();
    expect(
      wrapper.queryByTestId('resource-progress-dialog'),
    ).not.toBeInTheDocument();
  });

  it('shows the info menu after a click', () => {
    const store = createReduxStore({ stats: STATS });
    const wrapper = mountComponentWithStore(ResourceProgress, store, {
      parameters: PARAMETERS,
    });
    fireEvent.click(wrapper.container.querySelector('.selector'));

    expect(
      wrapper.queryByTestId('resource-progress-dialog'),
    ).toBeInTheDocument();
  });
});
