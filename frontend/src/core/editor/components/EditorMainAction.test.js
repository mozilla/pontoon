import sinon from 'sinon';

import * as user from 'core/user';
import * as history from 'modules/history';

import {
    createDefaultUser,
    createReduxStore,
    mountComponentWithStore,
} from 'test/store';

import * as editor from '..';
import EditorMainAction from './EditorMainAction';

function createComponent(sendTranslationMock?) {
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
        sinon.stub(history.actions, 'updateStatus').returns(updateStatusMock);
        sinon.stub(user.selectors, 'isTranslator').returns(true);
        sinon
            .stub(editor.selectors, 'sameExistingTranslation')
            .returns({ pk: 1 });

        const [wrapper] = createComponent();

        expect(wrapper.find('.action-approve')).toHaveLength(1);
        expect(wrapper.find('.action-suggest')).toHaveLength(0);
        expect(wrapper.find('.action-save')).toHaveLength(0);

        wrapper.find('.action-approve').simulate('click');
        expect(updateStatusMock.calledOnce).toBeTruthy();

        user.selectors.isTranslator.restore();
        editor.selectors.sameExistingTranslation.restore();
        history.actions.updateStatus.restore();
    });

    it('renders the Suggest button when force suggestion is on', () => {
        sinon.stub(user.selectors, 'isTranslator').returns(true);

        const sendTranslationMock = sinon.spy();
        const [wrapper, store] = createComponent(sendTranslationMock);

        createDefaultUser(store, { settings: { force_suggestions: true } });
        wrapper.update();

        expect(wrapper.find('.action-suggest')).toHaveLength(1);
        expect(wrapper.find('.action-approve')).toHaveLength(0);
        expect(wrapper.find('.action-save')).toHaveLength(0);

        wrapper.find('.action-suggest').simulate('click');
        expect(sendTranslationMock.calledOnce).toBeTruthy();

        user.selectors.isTranslator.restore();
    });

    it('renders the Suggest button when user does not have permission', () => {
        sinon.stub(user.selectors, 'isTranslator').returns(false);

        const [wrapper] = createComponent();

        expect(wrapper.find('.action-suggest')).toHaveLength(1);
        expect(wrapper.find('.action-save')).toHaveLength(0);
        expect(wrapper.find('.action-approve')).toHaveLength(0);

        user.selectors.isTranslator.restore();
    });

    it('shows a spinner and a disabled Suggesting button when running request', () => {
        sinon.stub(user.selectors, 'isTranslator').returns(true);

        const sendTranslationMock = sinon.spy();
        const [wrapper, store] = createComponent(sendTranslationMock);

        createDefaultUser(store, { settings: { force_suggestions: true } });
        store.dispatch(editor.actions.startUpdateTranslation());
        wrapper.update();

        expect(wrapper.find('.action-suggest')).toHaveLength(1);
        expect(wrapper.find('.action-suggest .fa-spin')).toHaveLength(1);

        wrapper.find('.action-suggest').simulate('click');
        expect(sendTranslationMock.calledOnce).toBeFalsy();

        user.selectors.isTranslator.restore();
    });

    it('renders the Save button when force suggestion is off and translation is not the same', () => {
        sinon.stub(user.selectors, 'isTranslator').returns(true);

        const sendTranslationMock = sinon.spy();
        const [wrapper] = createComponent(sendTranslationMock);

        expect(wrapper.find('.action-save')).toHaveLength(1);
        expect(wrapper.find('.action-suggest')).toHaveLength(0);
        expect(wrapper.find('.action-approve')).toHaveLength(0);

        wrapper.find('.action-save').simulate('click');
        expect(sendTranslationMock.calledOnce).toBeTruthy();

        user.selectors.isTranslator.restore();
    });

    it('shows a spinner and a disabled Saving button when running request', () => {
        sinon.stub(user.selectors, 'isTranslator').returns(true);

        const sendTranslationMock = sinon.spy();
        const [wrapper, store] = createComponent(sendTranslationMock);

        store.dispatch(editor.actions.startUpdateTranslation());
        wrapper.update();

        expect(wrapper.find('.action-save')).toHaveLength(1);
        expect(wrapper.find('.action-save .fa-spin')).toHaveLength(1);

        wrapper.find('.action-save').simulate('click');
        expect(sendTranslationMock.calledOnce).toBeFalsy();

        user.selectors.isTranslator.restore();
    });
});
