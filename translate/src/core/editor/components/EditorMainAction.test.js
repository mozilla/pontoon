import sinon from 'sinon';

import * as hookModule from '~/hooks/useTranslator';
import * as historyActions from '~/modules/history/actions';
import {
  createDefaultUser,
  createReduxStore,
  mountComponentWithStore,
} from '~/test/store';

import * as editorActions from '../actions';
import * as editorSelectors from '../selectors';
import EditorMainAction from './EditorMainAction';

beforeAll(() => sinon.stub(hookModule, 'useTranslator'));
beforeEach(() => hookModule.useTranslator.returns(true));
afterAll(() => hookModule.useTranslator.restore());

function createComponent(sendTranslationMock) {
  const store = createReduxStore();
  createDefaultUser(store);

  const comp = mountComponentWithStore(EditorMainAction, store, {
    sendTranslation: sendTranslationMock,
  });

  return [comp, store];
}

describe('<EditorMainAction>', () => {
  it('renders the Approve button when an identical translation exists', () => {
    const updateStatusMock = sinon.spy();
    sinon.stub(historyActions, 'updateStatus').returns(updateStatusMock);
    sinon.stub(editorSelectors, 'sameExistingTranslation').returns({ pk: 1 });

    try {
      const [wrapper] = createComponent();

      expect(wrapper.find('.action-approve')).toHaveLength(1);
      expect(wrapper.find('.action-suggest')).toHaveLength(0);
      expect(wrapper.find('.action-save')).toHaveLength(0);

      wrapper.find('.action-approve').simulate('click');
      expect(updateStatusMock.calledOnce).toBeTruthy();
    } finally {
      editorSelectors.sameExistingTranslation.restore();
      historyActions.updateStatus.restore();
    }
  });

  it('renders the Suggest button when force suggestion is on', () => {
    const sendTranslationMock = sinon.spy();
    const [wrapper, store] = createComponent(sendTranslationMock);

    createDefaultUser(store, { settings: { force_suggestions: true } });
    wrapper.update();

    expect(wrapper.find('.action-suggest')).toHaveLength(1);
    expect(wrapper.find('.action-approve')).toHaveLength(0);
    expect(wrapper.find('.action-save')).toHaveLength(0);

    wrapper.find('.action-suggest').simulate('click');
    expect(sendTranslationMock.calledOnce).toBeTruthy();
  });

  it('renders the Suggest button when user does not have permission', () => {
    hookModule.useTranslator.returns(false);

    const [wrapper] = createComponent();

    expect(wrapper.find('.action-suggest')).toHaveLength(1);
    expect(wrapper.find('.action-save')).toHaveLength(0);
    expect(wrapper.find('.action-approve')).toHaveLength(0);
  });

  it('shows a spinner and a disabled Suggesting button when running request', () => {
    const sendTranslationMock = sinon.spy();
    const [wrapper, store] = createComponent(sendTranslationMock);

    createDefaultUser(store, { settings: { force_suggestions: true } });
    store.dispatch(editorActions.startUpdateTranslation());
    wrapper.update();

    expect(wrapper.find('.action-suggest')).toHaveLength(1);
    expect(wrapper.find('.action-suggest .fa-spin')).toHaveLength(1);

    wrapper.find('.action-suggest').simulate('click');
    expect(sendTranslationMock.calledOnce).toBeFalsy();
  });

  it('renders the Save button when force suggestion is off and translation is not the same', () => {
    const sendTranslationMock = sinon.spy();
    const [wrapper] = createComponent(sendTranslationMock);

    expect(wrapper.find('.action-save')).toHaveLength(1);
    expect(wrapper.find('.action-suggest')).toHaveLength(0);
    expect(wrapper.find('.action-approve')).toHaveLength(0);

    wrapper.find('.action-save').simulate('click');
    expect(sendTranslationMock.calledOnce).toBeTruthy();
  });

  it('shows a spinner and a disabled Saving button when running request', () => {
    const sendTranslationMock = sinon.spy();
    const [wrapper, store] = createComponent(sendTranslationMock);

    store.dispatch(editorActions.startUpdateTranslation());
    wrapper.update();

    expect(wrapper.find('.action-save')).toHaveLength(1);
    expect(wrapper.find('.action-save .fa-spin')).toHaveLength(1);

    wrapper.find('.action-save').simulate('click');
    expect(sendTranslationMock.calledOnce).toBeFalsy();
  });
});
