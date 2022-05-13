/* eslint-env node */

import { createMemoryHistory } from 'history';
import { useEffect } from 'react';
import sinon from 'sinon';

import * as TranslationAPI from '~/api/translation';
import * as EditorActions from '~/core/editor/actions';
import { createReduxStore, mountComponentWithStore } from '~/test/store';

import { useUpdateTranslationStatus } from './useUpdateTranslationStatus';

const ENTITIES = [
  {
    pk: 42,
    original: 'le test',
    translation: [{ string: 'test', errors: [], warnings: [] }],
    project: { contact: '' },
    comment: '',
  },
];

function Wrapper({ id, change }) {
  const update = useUpdateTranslationStatus();
  useEffect(() => {
    update(id, change);
  }, []);
  return null;
}

function mountWrapper(props) {
  const history = createMemoryHistory({
    initialEntries: ['/kg/pro/all/?string=42'],
  });
  const initialState = {
    entities: { entities: ENTITIES },
    history: { translations: [] },
    otherlocales: { translations: [] },
    user: { settings: {}, username: 'Franck' },
  };
  const store = createReduxStore(initialState);
  const wrapper = mountComponentWithStore(Wrapper, store, props, history);
  return { history, store, wrapper };
}

describe('useUpdateTranslationStatus', () => {
  beforeAll(() => {
    global.fetch = () => Promise.resolve({ json: () => Promise.resolve({}) });
    sinon.stub(TranslationAPI, 'setTranslationStatus');
    sinon.stub(EditorActions, 'updateFailedChecks');
  });

  afterEach(() => {
    TranslationAPI.setTranslationStatus.reset();
    EditorActions.updateFailedChecks.reset();
  });

  afterAll(() => {
    delete global.fetch;
    TranslationAPI.setTranslationStatus.restore();
    EditorActions.updateFailedChecks.restore();
  });

  it('updates failed checks from response', async () => {
    TranslationAPI.setTranslationStatus.returns({
      string: 'string',
      failedChecks: 'FC',
    });
    EditorActions.updateFailedChecks.returns({ type: 'whatever' });

    mountWrapper({ id: 42, change: 'approve' });

    // Let the async code in useUpdateTranslationStatus run
    await 1;

    expect(TranslationAPI.setTranslationStatus.getCalls()).toMatchObject([
      { args: ['approve', 42, 'all', undefined] },
    ]);
    expect(EditorActions.updateFailedChecks.getCalls()).toMatchObject([
      { args: ['FC', 42] },
    ]);
  });
});
