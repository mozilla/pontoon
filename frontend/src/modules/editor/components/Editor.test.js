import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import * as user from 'core/user';
import * as editor from 'modules/editor';

import { EditorBase } from './Editor';
import EditorSettings from './EditorSettings';
import KeyboardShortcuts from './KeyboardShortcuts';


const SELECTED_ENTITY = {
    pk: 42,
    original: 'le test',
    original_plural: 'les tests',
    translation: [
        { string: 'test' },
        { string: 'test plural' },
    ],
};


function createEditorBase({
    pluralForm = -1,
    forceSuggestions = true,
    isAuthenticated = true,
    selectedEntity = SELECTED_ENTITY,
} = {}) {
    return shallow(<EditorBase
        dispatch={ () => {} }
        activeTranslation='initial'
        editor={
            { translation: '' }
        }
        locale={
            { code: 'kg' }
        }
        pluralForm={ pluralForm }
        selectedEntity={ selectedEntity }
        user={ {
            isAuthenticated,
            username: 'Sarevok',
            settings: {
                forceSuggestions,
            },
        } }
    />);
}


function expectHiddenSettingsAndActions(wrapper) {
    expect(wrapper.find('button')).toHaveLength(0);
    expect(wrapper.find(EditorSettings)).toHaveLength(0);
    expect(wrapper.find(KeyboardShortcuts)).toHaveLength(0);
    expect(wrapper.find('#editor-editor-button-copy')).toHaveLength(0);
}


describe('<EditorBase>', () => {
    beforeAll(() => {
        sinon.stub(editor.actions, 'sendTranslation').returns({ type: 'whatever' });
        sinon.stub(user.actions, 'saveSetting').returns({ type: 'whatever' });
    });

    afterEach(() => {
        editor.actions.sendTranslation.reset();
        user.actions.saveSetting.reset();
    });

    afterAll(() => {
        editor.actions.sendTranslation.restore();
        user.actions.saveSetting.restore();
    });

    it('renders correctly', () => {
        const wrapper = createEditorBase();

        // 3 buttons to control the editor.
        expect(wrapper.find('button')).toHaveLength(3);
    });

    it('has the active translation as content when created', () => {
        const wrapper = createEditorBase();
        expect(wrapper.state().translation).toEqual('initial');
    });

    it('clears the text when the Clear button is clicked', () => {
        const wrapper = createEditorBase();

        wrapper.find('.action-clear').simulate('click');
        expect(wrapper.state().translation).toEqual('');
    });

    it('copies the original string in the textarea when the Copy button is clicked', () => {
        const wrapper = createEditorBase();

        wrapper.find('.action-copy').simulate('click');
        expect(wrapper.state().translation).toEqual(SELECTED_ENTITY.original);
    });

    it('copies the plural original string in the textarea when the Copy button is clicked', () => {
        const wrapper = createEditorBase({ pluralForm: 5 });

        wrapper.find('.action-copy').simulate('click');
        expect(wrapper.state().translation).toEqual(SELECTED_ENTITY.original_plural);
    });

    it('calls the sendTranslation action when the Suggest button is clicked', () => {
        const wrapper = createEditorBase();

        wrapper.find('.action-suggest').simulate('click');
        expect(editor.actions.sendTranslation.calledOnce).toBeTruthy();
        expect(
            editor.actions.sendTranslation
            .calledWith(SELECTED_ENTITY.pk, 'initial', 'kg', SELECTED_ENTITY.original)
        ).toBeTruthy();
    });

    it('shows the Save button when forceSuggestions is off', () => {
        const wrapper = createEditorBase({ forceSuggestions: false });

        expect(wrapper.find('.action-save').exists()).toBeTruthy();
    });

    it('calls the sendTranslation action when the Save button is clicked', () => {
        const wrapper = createEditorBase({ forceSuggestions: false });

        wrapper.find('.action-save').simulate('click');
        expect(editor.actions.sendTranslation.calledOnce).toBeTruthy();
        expect(
            editor.actions.sendTranslation
            .calledWith(SELECTED_ENTITY.pk, 'initial', 'kg', SELECTED_ENTITY.original)
        ).toBeTruthy();
    });

    it('hides the settings and actions when the user is logged out', () => {
        const wrapper = createEditorBase({ isAuthenticated: false });

        expectHiddenSettingsAndActions(wrapper);

        expect(wrapper.find('#editor-editor-sign-in-to-translate')).toHaveLength(1);
    });

    it('hides the settings and actions when the entity is read-only', () => {
        const selectedEntity = {
            ...SELECTED_ENTITY,
            readonly: true,
        }
        const wrapper = createEditorBase({ selectedEntity });

        expectHiddenSettingsAndActions(wrapper);

        expect(wrapper.find('#editor-editor-read-only-localization')).toHaveLength(1);
    });

    it('dispatches the saveSetting action when updateSetting is called', () => {
        const wrapper = createEditorBase();

        wrapper.instance().updateSetting('setting', true);
        expect(user.actions.saveSetting.calledOnce).toBeTruthy();
        expect(
            user.actions.saveSetting
            .calledWith('setting', true, 'Sarevok')
        ).toBeTruthy();
    });
});
