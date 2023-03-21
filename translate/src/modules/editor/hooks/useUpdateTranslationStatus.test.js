/* eslint-env node */

import { createMemoryHistory } from 'history';
import React, { useEffect } from 'react';
import sinon from 'sinon';

import * as TranslationAPI from '~/api/translation';
import { EntityView } from '~/context/EntityView';
import { FailedChecksData } from '~/context/FailedChecksData';
import { createReduxStore, mountComponentWithStore } from '~/test/store';

import { useUpdateTranslationStatus } from './useUpdateTranslationStatus';

const ENTITY = {
  pk: 42,
  original: 'le test',
  translation: [{ string: 'test', errors: [], warnings: [] }],
  project: { contact: '' },
  comment: '',
};

function Wrapper({ id, change }) {
  const update = useUpdateTranslationStatus();
  useEffect(() => {
    update(id, change);
  }, []);
  return null;
}

function mountWrapper({ setFailedChecks, ...props }) {
  const history = createMemoryHistory({
    initialEntries: ['/kg/pro/all/?string=42'],
  });
  const initialState = {
    otherlocales: { translations: [] },
    user: { settings: {}, username: 'Franck' },
  };
  const store = createReduxStore(initialState);
  const wrapper = mountComponentWithStore(
    () => (
      <EntityView.Provider
        value={{
          entity: ENTITY,
          hasPluralForms: false,
          pluralForm: 0,
          setPluralForm: () => {},
        }}
      >
        <FailedChecksData.Provider value={{ setFailedChecks }}>
          <Wrapper {...props} />
        </FailedChecksData.Provider>
      </EntityView.Provider>
    ),
    store,
    {},
    history,
  );
  return { history, store, wrapper };
}

describe('useUpdateTranslationStatus', () => {
  beforeAll(() => {
    global.fetch = () => Promise.resolve({ json: () => Promise.resolve({}) });
    sinon.stub(TranslationAPI, 'setTranslationStatus');
  });

  afterEach(() => {
    TranslationAPI.setTranslationStatus.reset();
  });

  afterAll(() => {
    delete global.fetch;
    TranslationAPI.setTranslationStatus.restore();
  });

  it('updates failed checks from response', async () => {
    TranslationAPI.setTranslationStatus.returns({
      string: 'string',
      failedChecks: 'FC',
    });

    const setFailedChecks = sinon.stub();
    mountWrapper({ id: 42, change: 'approve', setFailedChecks });

    // Let the async code in useUpdateTranslationStatus run
    await 1;

    expect(TranslationAPI.setTranslationStatus.getCalls()).toMatchObject([
      { args: ['approve', 42, 'all', undefined] },
    ]);
    expect(setFailedChecks.getCalls()).toMatchObject([{ args: ['FC', 42] }]);
  });
});
