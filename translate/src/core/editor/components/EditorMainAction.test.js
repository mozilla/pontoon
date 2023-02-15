import * as Fluent from '@fluent/react';
import { mount } from 'enzyme';
import React from 'react';
import sinon from 'sinon';

import * as Hooks from '~/hooks';
import * as Translator from '~/hooks/useTranslator';

import * as ExistingTranslation from '../hooks/useExistingTranslationGetter';
import * as SendTranslation from '../hooks/useSendTranslation';
import * as UpdateTranslationStatus from '../hooks/useUpdateTranslationStatus';

import { EditorMainAction } from './EditorMainAction';

beforeAll(() => {
  sinon.stub(Fluent, 'Localized').callsFake(({ children }) => children);
  sinon.stub(React, 'useContext');
  sinon.stub(Hooks, 'useAppSelector');
  sinon.stub(Translator, 'useTranslator');
  sinon.stub(ExistingTranslation, 'useExistingTranslationGetter');
  sinon.stub(SendTranslation, 'useSendTranslation');
  sinon.stub(UpdateTranslationStatus, 'useUpdateTranslationStatus');
});
beforeEach(() => {
  Fluent.Localized.returns;
  React.useContext.returns({ busy: false }); // EditorData.busy
  Hooks.useAppSelector.returns(false); // user.settings.forceSuggestions
  Translator.useTranslator.returns(true);
  ExistingTranslation.useExistingTranslationGetter.returns(() => undefined);
  SendTranslation.useSendTranslation.returns(() => {});
  UpdateTranslationStatus.useUpdateTranslationStatus.returns(() => {});
});
afterAll(() => {
  Fluent.Localized.restore();
  React.useContext.restore();
  Hooks.useAppSelector.restore();
  Translator.useTranslator.restore();
  ExistingTranslation.useExistingTranslationGetter.restore();
  SendTranslation.useSendTranslation.restore();
  UpdateTranslationStatus.useUpdateTranslationStatus.restore();
});

describe('<EditorMainAction>', () => {
  it('renders the Approve button when an identical translation exists', () => {
    const spy = sinon.spy();
    UpdateTranslationStatus.useUpdateTranslationStatus.returns(spy);
    ExistingTranslation.useExistingTranslationGetter.returns(() => ({ pk: 1 }));

    const wrapper = mount(<EditorMainAction />);

    wrapper.find('.action-approve').simulate('click');
    expect(spy.getCalls()).toMatchObject([{ args: [1, 'approve', false] }]);
  });

  it('renders the Suggest button when force suggestion is on', () => {
    const spy = sinon.spy();
    SendTranslation.useSendTranslation.returns(spy);
    Hooks.useAppSelector.returns(true); // user.settings.forceSuggestions

    const wrapper = mount(<EditorMainAction />);

    wrapper.find('.action-suggest').simulate('click');
    expect(spy.getCalls()).toMatchObject([{ args: [] }]);
  });

  it('renders the Suggest button when user does not have permission', () => {
    Hooks.useAppSelector.returns(true); // user.settings.forceSuggestions

    const wrapper = mount(<EditorMainAction />);

    expect(wrapper.find('.action-suggest')).toHaveLength(1);
  });

  it('shows a spinner and a disabled Suggesting button when running request', () => {
    const spy = sinon.spy();
    SendTranslation.useSendTranslation.returns(spy);
    Hooks.useAppSelector.returns(true); // user.settings.forceSuggestions
    React.useContext.returns({ busy: true }); // EditorData.busy

    const wrapper = mount(<EditorMainAction />);

    expect(wrapper.find('.action-suggest .fa-spin')).toHaveLength(1);

    wrapper.find('.action-suggest').simulate('click');
    expect(spy.getCalls()).toMatchObject([]);
  });

  it('renders the Save button when force suggestion is off and translation is not the same', () => {
    const spy = sinon.spy();
    SendTranslation.useSendTranslation.returns(spy);

    const wrapper = mount(<EditorMainAction />);

    wrapper.find('.action-save').simulate('click');
    expect(spy.getCalls()).toMatchObject([{ args: [] }]);
  });

  it('shows a spinner and a disabled Saving button when running request', () => {
    const spy = sinon.spy();
    SendTranslation.useSendTranslation.returns(spy);
    React.useContext.returns({ busy: true }); // EditorData.busy

    const wrapper = mount(<EditorMainAction />);

    expect(wrapper.find('.action-save .fa-spin')).toHaveLength(1);

    wrapper.find('.action-save').simulate('click');
    expect(spy.getCalls()).toMatchObject([]);
  });
});
