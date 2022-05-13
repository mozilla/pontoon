/* eslint-env node */

import { createMemoryHistory } from 'history';
import { act } from 'react-dom/test-utils';
import sinon from 'sinon';

import * as editorActions from '~/core/editor/actions';
import { createReduxStore, mountComponentWithStore } from '~/test/store';

import { EntityDetails } from './EntityDetails';

const ENTITIES = [
  {
    pk: 42,
    original: 'le test',
    translation: [{ string: 'test', errors: [], warnings: [] }],
    project: { contact: '' },
    comment: '',
  },
  {
    pk: 1,
    original: 'something',
    translation: [
      {
        approved: true,
        string: 'quelque chose',
        errors: ['Error1'],
        warnings: ['Warning1'],
      },
    ],
    project: { contact: '' },
    comment: '',
  },
  {
    pk: 2,
    original: 'something',
    translation: [
      {
        pretranslated: true,
        string: 'quelque chose',
        errors: [],
        warnings: [],
      },
    ],
    project: { contact: '' },
    comment: '',
  },
];

function mockEntityDetails(pk) {
  const history = createMemoryHistory({
    initialEntries: [`/kg/pro/all/?string=${pk}`],
  });

  const initialState = {
    entities: { entities: ENTITIES },
    history: { translations: [] },
    otherlocales: { translations: [] },
    user: { settings: { forceSuggestions: true }, username: 'Franck' },
  };
  const store = createReduxStore(initialState);
  const wrapper = mountComponentWithStore(EntityDetails, store, {}, history);
  return { history, store, wrapper };
}

describe('<EntityDetails>', () => {
  beforeAll(() => {
    global.fetch = () =>
      Promise.resolve({
        json: () => Promise.resolve({}),
      });
    sinon
      .stub(editorActions, 'updateFailedChecks')
      .returns({ type: 'whatever' });
    sinon
      .stub(editorActions, 'resetFailedChecks')
      .returns({ type: 'whatever' });
  });

  afterEach(() => {
    editorActions.updateFailedChecks.reset();
    editorActions.updateFailedChecks.returns({ type: 'whatever' });
    editorActions.resetFailedChecks.reset();
    editorActions.resetFailedChecks.returns({ type: 'whatever' });
  });

  afterAll(() => {
    delete global.fetch;
    editorActions.updateFailedChecks.restore();
    editorActions.resetFailedChecks.restore();
  });

  it('shows an empty section when no entity is selected', () => {
    const { wrapper } = mockEntityDetails('');
    expect(wrapper.text()).toBe('');
  });

  it('loads the correct list of components', () => {
    const { wrapper } = mockEntityDetails(42);

    expect(wrapper.find('.entity-navigation')).toHaveLength(1);
    expect(wrapper.find('.metadata')).toHaveLength(1);
    expect(wrapper.find('.editor')).toHaveLength(1);
    expect(wrapper.find('Helpers')).toHaveLength(1);
  });

  it('shows failed checks for approved translations with errors or warnings', () => {
    const { history, wrapper } = mockEntityDetails(42);

    expect(editorActions.updateFailedChecks.calledOnce).toBeFalsy();
    expect(editorActions.resetFailedChecks.calledOnce).toBeTruthy();

    act(() => history.push(`/kg/pro/all/?string=1`));
    wrapper.update();

    expect(editorActions.updateFailedChecks.calledOnce).toBeTruthy();
    expect(editorActions.resetFailedChecks.calledOnce).toBeTruthy();
  });

  it('hides failed checks for pretranslated translations without errors or warnings', () => {
    const { history, wrapper } = mockEntityDetails(42);

    expect(editorActions.updateFailedChecks.calledOnce).toBeFalsy();
    expect(editorActions.resetFailedChecks.calledOnce).toBeTruthy();

    act(() => history.push(`/kg/pro/all/?string=2`));
    wrapper.update();

    expect(editorActions.updateFailedChecks.calledOnce).toBeFalsy();
    expect(editorActions.resetFailedChecks.calledTwice).toBeTruthy();
  });
});
