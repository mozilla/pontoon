import React from 'react';
import sinon from 'sinon';

import { Locale } from '~/context/Locale';
import { updateFailedChecks } from '~/core/editor/actions';

import {
  createDefaultUser,
  createReduxStore,
  mountComponentWithStore,
} from '~/test/store';

import { FailedChecks } from './FailedChecks';

function createFailedChecks(user) {
  const store = createReduxStore({ project: { slug: 'firefox', tags: [] } });
  createDefaultUser(store, user);

  const Component = () => (
    <Locale.Provider value={{ code: 'kg' }}>
      <FailedChecks sendTranslation={sinon.mock()} />
    </Locale.Provider>
  );
  const comp = mountComponentWithStore(Component, store);

  return [comp, store];
}

describe('<FailedChecks>', () => {
  it('does not render if no errors or warnings present', () => {
    const [wrapper] = createFailedChecks();

    expect(wrapper.find('.failed-checks')).toHaveLength(0);
  });

  it('renders popup with errors and warnings', () => {
    const [wrapper, store] = createFailedChecks();

    store.dispatch(
      updateFailedChecks(
        {
          clErrors: ['one error'],
          pndbWarnings: ['a warning', 'two warnings'],
        },
        '',
      ),
    );
    wrapper.update();

    expect(wrapper.find('.failed-checks')).toHaveLength(1);
    expect(wrapper.find('#editor-FailedChecks--close')).toHaveLength(1);
    expect(wrapper.find('#editor-FailedChecks--title')).toHaveLength(1);
    expect(wrapper.find('.error')).toHaveLength(1);
    expect(wrapper.find('.warning')).toHaveLength(2);
  });

  it('renders save anyway button if translation with warnings submitted', () => {
    const [wrapper, store] = createFailedChecks({
      settings: { force_suggestions: false },
    });

    store.dispatch(
      updateFailedChecks({ pndbWarnings: ['a warning'] }, 'submitted'),
    );
    wrapper.update();

    expect(wrapper.find('.save.anyway')).toHaveLength(1);
  });

  it('renders suggest anyway button if translation with warnings suggested', () => {
    const [wrapper, store] = createFailedChecks({
      settings: { force_suggestions: true },
    });

    store.dispatch(
      updateFailedChecks({ pndbWarnings: ['a warning'] }, 'submitted'),
    );
    wrapper.update();

    expect(wrapper.find('.suggest.anyway')).toHaveLength(1);
  });

  it('renders suggest anyway button if user does not have sufficient permissions', () => {
    const [wrapper, store] = createFailedChecks({ manager_for_locales: [] });

    store.dispatch(
      updateFailedChecks({ pndbWarnings: ['a warning'] }, 'submitted'),
    );
    wrapper.update();

    expect(wrapper.find('.suggest.anyway')).toHaveLength(1);
  });

  it('renders approve anyway button if translation with warnings approved', () => {
    const [wrapper, store] = createFailedChecks();

    store.dispatch(updateFailedChecks({ pndbWarnings: ['a warning'] }, ''));
    wrapper.update();

    expect(wrapper.find('.approve.anyway')).toHaveLength(1);
  });
});
