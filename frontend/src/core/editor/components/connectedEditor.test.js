import React from 'react';
import { mount } from 'enzyme';
import sinon from 'sinon';

import { createReduxStore } from 'test/store';

import * as user from 'core/user';

import { actions } from '..';

import connectedEditor from './connectedEditor';


const SELECTED_ENTITY = {
    pk: 42,
    original: 'le test',
    original_plural: 'les tests',
    translation: [
        { string: 'test' },
        { string: 'test plural' },
    ],
};

const ENTITIES = [
    SELECTED_ENTITY,
    {
        pk: 1,
        original: 'something',
        translation: [{
            string: 'quelque chose',
        }],
    },
];


class FakeEditor extends React.Component {
    render() {
        return <div>
            <p>Hello</p>
            <button className='clear' onClick={ this.props.clearEditor } />
            <button className='copy' onClick={ this.props.copyOriginalIntoEditor } />
            <button className='save' onClick={ this.props.sendTranslation } />
            <button className='settings' onClick={
                () => this.props.updateSetting('setting', true)
            } />
        </div>;
    }
}
const FakeConnectedEditor = connectedEditor(FakeEditor);


function createEditorBase({
    pluralForm = -1,
} = {}) {
    const initialState = {
        entities: {
            entities: ENTITIES,
        },
        router: {
            location: {
                pathname: '/kg/pro/all-resources/',
                search: '?string=' + ENTITIES[0].pk,
            },
        },
        locale: {
            code: 'kg',
        },
        plural: {
            pluralForm,
        },
    };
    const store = createReduxStore(initialState);
    return mount(<FakeConnectedEditor
        store={ store }
    />);
}


describe('connectedEditor', () => {
    beforeAll(() => {
        sinon.stub(actions, 'sendTranslation').returns({ type: 'whatever' });
        sinon.spy(actions, 'update');
        sinon.stub(user.actions, 'saveSetting').returns({ type: 'whatever' });
    });

    afterEach(() => {
        actions.sendTranslation.resetHistory();
        actions.update.resetHistory();
        user.actions.saveSetting.resetHistory();
    });

    afterAll(() => {
        actions.sendTranslation.restore();
        actions.update.restore();
        user.actions.saveSetting.restore();
    });

    it('renders correctly', () => {
        const wrapper = createEditorBase();
        expect(wrapper.text()).toEqual('Hello');
    });

    it('clears the text when the clearEditor prop is called', () => {
        const wrapper = createEditorBase();

        wrapper.find('.clear').simulate('click');
        expect(actions.update.calledOnce).toBeTruthy();
        expect(actions.update.calledWith('')).toBeTruthy();
    });

    it('copies the original string when the copyOriginalIntoEditor prop is called', () => {
        const wrapper = createEditorBase();

        wrapper.find('.copy').simulate('click');
        expect(actions.update.calledOnce).toBeTruthy();
        expect(actions.update.calledWith(SELECTED_ENTITY.original)).toBeTruthy();
    });

    it('copies the plural string when the copyOriginalIntoEditor prop is called', () => {
        const wrapper = createEditorBase({ pluralForm: 1 });

        wrapper.find('.copy').simulate('click');
        expect(actions.update.calledOnce).toBeTruthy();
        expect(actions.update.calledWith(SELECTED_ENTITY.original_plural)).toBeTruthy();
    });

    it('calls the sendTranslation action when the sendTranslation prop is called', () => {
        const wrapper = createEditorBase();

        wrapper.find('.save').simulate('click');
        expect(actions.sendTranslation.calledOnce).toBeTruthy();
    });

    it('calls the saveSetting action when the updateSetting prop is called', () => {
        const wrapper = createEditorBase();

        wrapper.find('.settings').simulate('click');
        expect(user.actions.saveSetting.calledOnce).toBeTruthy();
    });
});
