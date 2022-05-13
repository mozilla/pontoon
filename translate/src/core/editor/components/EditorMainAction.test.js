import sinon from 'sinon';

import * as UpdateTranslationStatus from '~/core/editor/hooks/useUpdateTranslationStatus';
import * as Translator from '~/hooks/useTranslator';
import {
  createDefaultUser,
  createReduxStore,
  mountComponentWithStore,
} from '~/test/store';

import * as editorActions from '../actions';
import * as ExistingTranslation from '../hooks/useExistingTranslation';
import { EditorMainAction } from './EditorMainAction';

beforeAll(() => {
  sinon.stub(Translator, 'useTranslator');
  sinon.stub(ExistingTranslation, 'useExistingTranslation');
});
beforeEach(() => {
  Translator.useTranslator.returns(true);
  ExistingTranslation.useExistingTranslation.returns(undefined);
});
afterAll(() => {
  Translator.useTranslator.restore();
  ExistingTranslation.useExistingTranslation.restore();
});

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
    const spy = sinon.spy();
    sinon
      .stub(UpdateTranslationStatus, 'useUpdateTranslationStatus')
      .returns(spy);
    ExistingTranslation.useExistingTranslation.returns({ pk: 1 });

    try {
      const [wrapper] = createComponent();

      expect(wrapper.find('.action-approve')).toHaveLength(1);
      expect(wrapper.find('.action-suggest')).toHaveLength(0);
      expect(wrapper.find('.action-save')).toHaveLength(0);

      wrapper.find('.action-approve').simulate('click');
      expect(spy.calledOnce).toBeTruthy();
    } finally {
      UpdateTranslationStatus.useUpdateTranslationStatus.restore();
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
    Translator.useTranslator.returns(false);

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
