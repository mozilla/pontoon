import React from 'react';

import { FailedChecksData } from '~/context/FailedChecksData';
import { Locale } from '~/context/Locale';

import {
  createDefaultUser,
  createReduxStore,
  mountComponentWithStore,
} from '~/test/store';

import { FailedChecks } from './FailedChecks';
import { vi, expect } from 'vitest';

function mountFailedChecks(failedChecks, user) {
  const store = createReduxStore({ project: { slug: 'firefox', tags: [] } });
  createDefaultUser(store, user);

  const Component = () => (
    <Locale.Provider value={{ code: 'kg' }}>
      <FailedChecksData.Provider value={failedChecks}>
        <FailedChecks sendTranslation={vi.fn()} />
      </FailedChecksData.Provider>
    </Locale.Provider>
  );
  return mountComponentWithStore(Component, store);
}

describe('<FailedChecks>', () => {
  it('does not render if no errors or warnings present', () => {
    const wrapper = mountFailedChecks({ errors: [], warnings: [] });

    expect(
      wrapper.container.querySelector('.failed-checks'),
    ).not.toBeInTheDocument();
  });

  it('renders popup with errors and warnings', () => {
    const wrapper = mountFailedChecks({
      errors: ['one error'],
      warnings: ['a warning', 'two warnings'],
    });

    expect(wrapper.container.querySelectorAll('.failed-checks')).toHaveLength(
      1,
    );
    expect(wrapper.queryByRole('button')).toHaveTextContent('×');
    expect(wrapper.container.querySelectorAll('p.title')).toHaveLength(1);
    expect(wrapper.container.querySelectorAll('.error')).toHaveLength(1);
    expect(wrapper.container.querySelectorAll('.warning')).toHaveLength(2);
  });

  it('renders save anyway button if translation with warnings submitted', () => {
    const wrapper = mountFailedChecks(
      { errors: [], warnings: ['a warning'], source: 'submitted' },
      { settings: { force_suggestions: false } },
    );

    expect(wrapper.container.querySelector('.save.anyway')).toBeInTheDocument();
  });

  it('renders suggest anyway button if translation with warnings suggested', () => {
    const wrapper = mountFailedChecks(
      { errors: [], warnings: ['a warning'], source: 'submitted' },
      { settings: { force_suggestions: true } },
    );

    expect(
      wrapper.container.querySelector('.suggest.anyway'),
    ).toBeInTheDocument();
  });

  it('renders suggest anyway button if user does not have sufficient permissions', () => {
    const wrapper = mountFailedChecks(
      { errors: [], warnings: ['a warning'], source: 'submitted' },
      { can_manage_locales: [] },
    );

    expect(
      wrapper.container.querySelector('.suggest.anyway'),
    ).toBeInTheDocument();
  });

  it('renders approve anyway button if translation with warnings approved', () => {
    const wrapper = mountFailedChecks({
      errors: [],
      warnings: ['a warning'],
      source: 42,
    });

    expect(
      wrapper.container.querySelector('.approve.anyway'),
    ).toBeInTheDocument();
  });
});
