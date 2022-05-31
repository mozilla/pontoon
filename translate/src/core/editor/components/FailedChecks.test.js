import React from 'react';
import sinon from 'sinon';

import { FailedChecksData } from '~/context/FailedChecksData';
import { Locale } from '~/context/Locale';

import {
  createDefaultUser,
  createReduxStore,
  mountComponentWithStore,
} from '~/test/store';

import { FailedChecks } from './FailedChecks';

function mountFailedChecks(failedChecks, user) {
  const store = createReduxStore({ project: { slug: 'firefox', tags: [] } });
  createDefaultUser(store, user);

  const Component = () => (
    <Locale.Provider value={{ code: 'kg' }}>
      <FailedChecksData.Provider value={failedChecks}>
        <FailedChecks sendTranslation={sinon.mock()} />
      </FailedChecksData.Provider>
    </Locale.Provider>
  );
  return mountComponentWithStore(Component, store);
}

describe('<FailedChecks>', () => {
  it('does not render if no errors or warnings present', () => {
    const wrapper = mountFailedChecks({ errors: [], warnings: [] });

    expect(wrapper.find('.failed-checks')).toHaveLength(0);
  });

  it('renders popup with errors and warnings', () => {
    const wrapper = mountFailedChecks({
      errors: ['one error'],
      warnings: ['a warning', 'two warnings'],
    });

    expect(wrapper.find('.failed-checks')).toHaveLength(1);
    expect(wrapper.find('#editor-FailedChecks--close')).toHaveLength(1);
    expect(wrapper.find('#editor-FailedChecks--title')).toHaveLength(1);
    expect(wrapper.find('.error')).toHaveLength(1);
    expect(wrapper.find('.warning')).toHaveLength(2);
  });

  it('renders save anyway button if translation with warnings submitted', () => {
    const wrapper = mountFailedChecks(
      { errors: [], warnings: ['a warning'], source: 'submitted' },
      { settings: { force_suggestions: false } },
    );

    expect(wrapper.find('.save.anyway')).toHaveLength(1);
  });

  it('renders suggest anyway button if translation with warnings suggested', () => {
    const wrapper = mountFailedChecks(
      { errors: [], warnings: ['a warning'], source: 'submitted' },
      { settings: { force_suggestions: true } },
    );

    expect(wrapper.find('.suggest.anyway')).toHaveLength(1);
  });

  it('renders suggest anyway button if user does not have sufficient permissions', () => {
    const wrapper = mountFailedChecks(
      { errors: [], warnings: ['a warning'], source: 'submitted' },
      { manager_for_locales: [] },
    );

    expect(wrapper.find('.suggest.anyway')).toHaveLength(1);
  });

  it('renders approve anyway button if translation with warnings approved', () => {
    const wrapper = mountFailedChecks({
      errors: [],
      warnings: ['a warning'],
      source: 42,
    });

    expect(wrapper.find('.approve.anyway')).toHaveLength(1);
  });
});
