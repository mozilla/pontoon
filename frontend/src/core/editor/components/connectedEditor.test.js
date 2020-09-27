import React from 'react';
import { mount } from 'enzyme';
import sinon from 'sinon';

import { createReduxStore } from 'test/store';

import * as user from 'core/user';
import * as history from 'modules/history';
import * as unsavedchanges from 'modules/unsavedchanges';

import { actions } from '..';

import connectedEditor from './connectedEditor';

const SELECTED_ENTITY = {
    pk: 42,
    original: 'le test',
    original_plural: 'les tests',
    translation: [
        { string: 'test', pk: 2 },
        { string: 'test plural', pk: 3 },
    ],
};

const ENTITIES = [
    SELECTED_ENTITY,
    {
        pk: 1,
        original: 'something',
        translation: [
            {
                string: 'quelque chose',
            },
        ],
    },
];

class FakeEditor extends React.Component {
    render() {
        return (
            <div>
                <p>Hello</p>
                <textarea onKeyDown={this.props.handleShortcuts} />
                <button className='clear' onClick={this.props.clearEditor} />
                <button
                    className='copy'
                    onClick={this.props.copyOriginalIntoEditor}
                />
                <button className='save' onClick={this.props.sendTranslation} />
                <button
                    className='settings'
                    onClick={() => this.props.updateSetting('setting', true)}
                />
            </div>
        );
    }
}
const FakeConnectedEditor = connectedEditor(FakeEditor);

function createEditorBase({
    pluralForm = -1,
    errors = [],
    warnings = [],
    translation = 'hello',
    initialTranslation = '',
    source = '',
    unsavedchanges = { shown: false },
} = {}) {
    const initialState = {
        editor: {
            errors,
            warnings,
            source,
            translation,
            initialTranslation,
        },
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
        user: {
            username: 'michael_umanah',
            isAuthenticated: true,
            settings: {
                forceSuggestions: false,
            },
            managerForLocales: [],
            translatorForProjects: {},
            translatorForLocales: [],
        },
        unsavedchanges,
    };
    const store = createReduxStore(initialState);
    return mount(<FakeConnectedEditor store={store} />);
}

describe('connectedEditor', () => {
    beforeAll(() => {
        sinon.stub(actions, 'resetFailedChecks').returns({ type: 'whatever' });
        sinon.stub(actions, 'sendTranslation').returns({ type: 'whatever' });
        sinon.spy(actions, 'update');
        sinon.stub(user.actions, 'saveSetting').returns({ type: 'whatever' });
        sinon
            .stub(history.actions, 'updateStatus')
            .returns({ type: 'whatever' });
        sinon
            .stub(unsavedchanges.actions, 'hide')
            .returns({ type: 'whatever' });
        sinon
            .stub(unsavedchanges.actions, 'ignore')
            .returns({ type: 'whatever' });
    });

    afterEach(() => {
        actions.resetFailedChecks.resetHistory();
        actions.sendTranslation.resetHistory();
        actions.update.resetHistory();
        user.actions.saveSetting.resetHistory();
        history.actions.updateStatus.resetHistory();
        unsavedchanges.actions.hide.resetHistory();
        unsavedchanges.actions.ignore.resetHistory();
    });

    afterAll(() => {
        actions.resetFailedChecks.restore();
        actions.sendTranslation.restore();
        actions.update.restore();
        user.actions.saveSetting.restore();
        history.actions.updateStatus.restore();
        unsavedchanges.actions.hide.restore();
        unsavedchanges.actions.ignore.restore();
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
        expect(
            actions.update.calledWith(SELECTED_ENTITY.original),
        ).toBeTruthy();
    });

    it('copies the plural string when the copyOriginalIntoEditor prop is called', () => {
        const wrapper = createEditorBase({ pluralForm: 1 });

        wrapper.find('.copy').simulate('click');
        expect(actions.update.calledOnce).toBeTruthy();
        expect(
            actions.update.calledWith(SELECTED_ENTITY.original_plural),
        ).toBeTruthy();
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

    it('sends the translation on Enter', () => {
        const wrapper = createEditorBase();

        const event = {
            preventDefault: sinon.spy(),
            keyCode: 13, // Enter
            altKey: false,
            ctrlKey: false,
            shiftKey: false,
        };

        expect(actions.sendTranslation.called).toBeFalsy();
        wrapper.find('textarea').simulate('keydown', event);
        expect(actions.sendTranslation.called).toBeTruthy();
    });

    it('approves the translation on Enter if failed checks triggered by approval', () => {
        const wrapper = createEditorBase({
            errors: ['error1'],
            warnings: ['warning1'],
            source: 1,
        });

        const event = {
            preventDefault: sinon.spy(),
            keyCode: 13, // Enter
            altKey: false,
            ctrlKey: false,
            shiftKey: false,
        };

        expect(history.actions.updateStatus.called).toBeFalsy();
        wrapper.find('textarea').simulate('keydown', event);
        expect(history.actions.updateStatus.called).toBeTruthy();
    });

    it('approves the translation on Enter if an identical translation exists', () => {
        const translation = SELECTED_ENTITY.translation[0].string;
        const wrapper = createEditorBase({
            errors: ['error1'],
            warnings: ['warning1'],
            translation: translation,
            initialTranslation: translation,
        });

        const event = {
            preventDefault: sinon.spy(),
            keyCode: 13, // Enter
            altKey: false,
            ctrlKey: false,
            shiftKey: false,
        };

        expect(history.actions.updateStatus.called).toBeFalsy();
        wrapper.find('textarea').simulate('keydown', event);
        expect(history.actions.updateStatus.called).toBeTruthy();
    });

    it('ignores unsaved changes on Enter if unsaved changes popup is shown', () => {
        const wrapper = createEditorBase({
            unsavedchanges: { shown: true },
        });

        const event = {
            preventDefault: sinon.spy(),
            keyCode: 13, // Enter
            altKey: false,
            ctrlKey: false,
            shiftKey: false,
        };

        expect(unsavedchanges.actions.ignore.called).toBeFalsy();
        wrapper.find('textarea').simulate('keydown', event);
        expect(unsavedchanges.actions.ignore.called).toBeTruthy();
    });

    it('closes unsaved changes popup if open on Esc', () => {
        const wrapper = createEditorBase({
            unsavedchanges: { shown: true },
        });

        const event = {
            preventDefault: sinon.spy(),
            keyCode: 27, // Esc
        };

        expect(unsavedchanges.actions.hide.called).toBeFalsy();
        wrapper.find('textarea').simulate('keydown', event);
        expect(unsavedchanges.actions.hide.called).toBeTruthy();
    });

    it('closes failed checks popup if open on Esc', () => {
        const wrapper = createEditorBase({
            errors: ['error1'],
            warnings: ['warning1'],
        });

        const event = {
            preventDefault: sinon.spy(),
            keyCode: 27, // Esc
        };

        expect(actions.resetFailedChecks.called).toBeFalsy();
        wrapper.find('textarea').simulate('keydown', event);
        expect(actions.resetFailedChecks.called).toBeTruthy();
    });

    it('copies the original into the Editor on Ctrl + Shift + C', () => {
        const wrapper = createEditorBase();

        const event = {
            preventDefault: sinon.spy(),
            keyCode: 67, // C
            altKey: false,
            ctrlKey: true,
            shiftKey: true,
        };

        expect(actions.update.called).toBeFalsy();
        wrapper.find('textarea').simulate('keydown', event);
        expect(actions.update.called).toBeTruthy();
        expect(
            actions.update.calledWith(SELECTED_ENTITY.original),
        ).toBeTruthy();
    });

    it('clears the translation on Ctrl + Shift + Backspace', () => {
        const wrapper = createEditorBase();

        const event = {
            preventDefault: sinon.spy(),
            keyCode: 8, // Backspace
            altKey: false,
            ctrlKey: true,
            shiftKey: true,
        };

        expect(actions.update.called).toBeFalsy();
        wrapper.find('textarea').simulate('keydown', event);
        expect(actions.update.called).toBeTruthy();
        expect(actions.update.calledWith('')).toBeTruthy();
    });
});
