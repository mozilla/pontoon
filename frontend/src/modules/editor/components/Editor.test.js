import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import Editor from './Editor';
import EditorSettings from './EditorSettings';
import KeyboardShortcuts from './KeyboardShortcuts';


const TRANSLATION = 'test';
const TRANSLATION_PLURAL = 'test plural';
const SELECTED_ENTITY = {
    pk: 42,
    original: 'le test',
    original_plural: 'les tests',
    translation: [
        { string: TRANSLATION },
        { string: TRANSLATION_PLURAL },
    ],
};


function createShallowEditor({
    suggestMock,
    updateMock,
    pluralForm = -1,
    forceSuggestions = true,
    isAuthenticated = true,
} = {}) {
    return shallow(<Editor
        translation={ (Math.abs(pluralForm) !== 1) ? TRANSLATION_PLURAL : TRANSLATION }
        entity={ SELECTED_ENTITY }
        sendTranslation={ suggestMock }
        updateEditorTranslation={ updateMock }
        pluralForm={ pluralForm }
        user={ {
            isAuthenticated,
            settings: {
                forceSuggestions,
            },
        } }
    />);
}


describe('<Editor>', () => {
    it('renders correctly', () => {
        const wrapper = createShallowEditor();

        // 3 buttons to control the editor.
        expect(wrapper.find('button')).toHaveLength(3);
    });

    it('clears the text when the Clear button is clicked', () => {
        const updateMock = sinon.spy();
        const wrapper = createShallowEditor({ updateMock });

        wrapper.find('.action-clear').simulate('click');
        expect(updateMock.calledOnce).toBeTruthy();
        expect(updateMock.calledWith('')).toBeTruthy();
    });

    it('copies the original string in the textarea when the Copy button is clicked', () => {
        const updateMock = sinon.spy();
        const wrapper = createShallowEditor({ updateMock });

        wrapper.find('.action-copy').simulate('click');
        expect(updateMock.calledOnce).toBeTruthy();
        expect(updateMock.calledWith(SELECTED_ENTITY.original)).toBeTruthy();
    });

    it('copies the plural original string in the textarea when the Copy button is clicked', () => {
        const updateMock = sinon.spy();
        const wrapper = createShallowEditor({ updateMock, pluralForm: 5 });

        wrapper.find('.action-copy').simulate('click');
        expect(updateMock.calledOnce).toBeTruthy();
        expect(updateMock.calledWith(SELECTED_ENTITY.original_plural)).toBeTruthy();
    });

    it('calls the suggest action when the Suggest button is clicked', () => {
        const suggestMock = sinon.spy();
        const wrapper = createShallowEditor({ suggestMock });

        wrapper.find('.action-suggest').simulate('click');
        expect(suggestMock.calledOnce).toBeTruthy();
    });

    it('shows the Save button when forceSuggestions is off', () => {
        const suggestMock = sinon.spy();
        const wrapper = createShallowEditor({ suggestMock, pluralForm: -1, forceSuggestions: false });

        expect(wrapper.find('.action-save').exists()).toBeTruthy();
        wrapper.find('.action-save').simulate('click');
        expect(suggestMock.calledOnce).toBeTruthy();
    });

    it('calls the suggest action when the Save button is clicked', () => {
        const suggestMock = sinon.spy();
        const wrapper = createShallowEditor({ suggestMock, pluralForm: -1, forceSuggestions: false });

        wrapper.find('.action-save').simulate('click');
        expect(suggestMock.calledOnce).toBeTruthy();
    });

    it('hides the settings and actions when the user is logged out', () => {
        const wrapper = createShallowEditor({ isAuthenticated: false });

        expect(wrapper.find(EditorSettings)).toHaveLength(0);
        expect(wrapper.find(KeyboardShortcuts)).toHaveLength(0);
        expect(wrapper.find('#editor-editor-button-copy')).toHaveLength(0);

        expect(wrapper.find('#editor-editor-sign-in-to-translate')).toHaveLength(1);
    });
});
