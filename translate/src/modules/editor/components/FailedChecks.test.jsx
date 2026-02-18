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
    const errors = ['one error'];
    const warnings = ['a warning', 'two warnings'];
    const { container, getByRole, getByText } = mountFailedChecks({
      errors,
      warnings,
    });

    expect(container.querySelector('.failed-checks')).toBeInTheDocument();
    expect(getByRole('button', { name: /Close/i })).toHaveTextContent('×');
    getByText('THE FOLLOWING CHECKS HAVE FAILED');

    for (const error of errors) {
      getByText(error);
    }

    for (const warning of warnings) {
      getByText(warning);
    }
  });

  it('renders save anyway button if translation with warnings submitted', () => {
    const { getByRole } = mountFailedChecks(
      { errors: [], warnings: ['a warning'], source: 'submitted' },
      { settings: { force_suggestions: false } },
    );

    getByRole('button', { name: /save anyway/i });
  });

  it('renders suggest anyway button if translation with warnings suggested', () => {
    const { getByRole } = mountFailedChecks(
      { errors: [], warnings: ['a warning'], source: 'submitted' },
      { settings: { force_suggestions: true } },
    );

    getByRole('button', { name: /suggest anyway/i });
  });

  it('renders suggest anyway button if user does not have sufficient permissions', () => {
    const { getByRole } = mountFailedChecks(
      { errors: [], warnings: ['a warning'], source: 'submitted' },
      { can_manage_locales: [] },
    );

    getByRole('button', { name: /suggest anyway/i });
  });

  it('renders approve anyway button if translation with warnings approved', () => {
    const { getByRole } = mountFailedChecks({
      errors: [],
      warnings: ['a warning'],
      source: 42,
    });

    getByRole('button', { name: /approve anyway/i });
  });
});
