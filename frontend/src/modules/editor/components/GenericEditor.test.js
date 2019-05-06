import React from 'react';
import { mount, shallow } from 'enzyme';
import sinon from 'sinon';

import { GenericEditorBase } from './GenericEditor';


const DEFAULT_LOCALE = {
    direction: 'ltr',
    code: 'kg',
    script: 'Latin',
};

const EDITOR = {
    translation: 'world',
    errors: [],
    warnings: [],
};


describe('<GenericEditorBase>', () => {
    it('renders a textarea with some content', () => {
        const wrapper = shallow(<GenericEditorBase
            editor={ EDITOR }
            locale={ DEFAULT_LOCALE }
        />);

        expect(wrapper.find('textarea')).toHaveLength(1);
        expect(wrapper.find('textarea').html()).toContain('world');
    });

    it('calls the updateTranslation function on change', () => {
        const mockUpdate = sinon.spy();
        const wrapper = shallow(<GenericEditorBase
            editor={ EDITOR }
            locale={ DEFAULT_LOCALE }
            updateTranslation={ mockUpdate }
        />);

        expect(mockUpdate.called).toBeFalsy();
        wrapper.find('textarea').simulate('change', { currentTarget: { value: 'good bye' } });
        expect(mockUpdate.called).toBeTruthy();
    });

    it('updates the translation when selectionReplacementContent is passed', () => {
        const resetMock = sinon.stub();
        const updateMock = sinon.stub();

        const wrapper = mount(<GenericEditorBase
            editor={ EDITOR }
            locale={ DEFAULT_LOCALE }
            resetSelectionContent={ resetMock }
            updateTranslation={ updateMock }
        />);

        wrapper.setProps({ editor: { selectionReplacementContent: 'hello ' } });

        expect(updateMock.calledOnce).toBeTruthy();
        expect(updateMock.calledWith('hello world')).toBeTruthy();
        expect(resetMock.calledOnce).toBeTruthy();
    });

    it('sends the translation on Enter', () => {
        const mockSend = sinon.spy();
        const wrapper = shallow(<GenericEditorBase
            editor={ EDITOR }
            locale={ DEFAULT_LOCALE }
            sendTranslation={ mockSend }
            disableAction={ sinon.spy() }
        />);

        const event = {
            preventDefault: sinon.spy(),
            keyCode: 13,  // Enter
            altKey: false,
            ctrlKey: false,
            shiftKey: false,
        };

        expect(mockSend.calledOnce).toBeFalsy();
        wrapper.find('textarea').simulate('keydown', event);
        expect(mockSend.calledOnce).toBeTruthy();
    });

    it('approves the translation on Enter if failed checks triggered by approval', () => {
        const mockSend = sinon.spy();

        const editor = {
            ...EDITOR,
            errors: ['error1'],
            warnings: ['warning1'],
            source: 1,
        }

        const wrapper = shallow(<GenericEditorBase
            editor={ editor }
            locale={ DEFAULT_LOCALE }
            updateTranslationStatus={ mockSend }
            disableAction={ sinon.spy() }
        />);

        const event = {
            preventDefault: sinon.spy(),
            keyCode: 13,  // Enter
            altKey: false,
            ctrlKey: false,
            shiftKey: false,
        };

        expect(mockSend.calledOnce).toBeFalsy();
        wrapper.find('textarea').simulate('keydown', event);
        expect(mockSend.calledOnce).toBeTruthy();
    });

    it('closes failed checks popup if open on Esc', () => {
        const mockSend = sinon.spy();

        const editor = {
            ...EDITOR,
            errors: ['error1'],
            warnings: ['warning1'],
        }

        const wrapper = shallow(<GenericEditorBase
            editor={ editor }
            locale={ DEFAULT_LOCALE }
            resetFailedChecks={ mockSend }
        />);

        const event = {
            preventDefault: sinon.spy(),
            keyCode: 27,  // Esc
        };

        expect(mockSend.calledOnce).toBeFalsy();
        wrapper.find('textarea').simulate('keydown', event);
        expect(mockSend.calledOnce).toBeTruthy();
    });

    it('copies the original into the Editor on Ctrl + Shift + C', () => {
        const mockCopy = sinon.spy();
        const wrapper = shallow(<GenericEditorBase
            editor={ EDITOR }
            locale={ DEFAULT_LOCALE }
            copyOriginalIntoEditor={ mockCopy }
        />);

        const event = {
            preventDefault: sinon.spy(),
            keyCode: 67,  // C
            altKey: false,
            ctrlKey: true,
            shiftKey: true,
        };

        expect(mockCopy.calledOnce).toBeFalsy();
        wrapper.find('textarea').simulate('keydown', event);
        expect(mockCopy.calledOnce).toBeTruthy();
    });

    it('clears the translation on Ctrl + Shift + Backspace', () => {
        const mockUpdate = sinon.spy();
        const wrapper = shallow(<GenericEditorBase
            editor={ EDITOR }
            locale={ DEFAULT_LOCALE }
            updateTranslation={ mockUpdate }
        />);

        const event = {
            preventDefault: sinon.spy(),
            keyCode: 8,  // Backspace
            altKey: false,
            ctrlKey: true,
            shiftKey: true,
        };

        expect(mockUpdate.calledOnce).toBeFalsy();
        wrapper.find('textarea').simulate('keydown', event);
        expect(mockUpdate.calledOnce).toBeTruthy();
        expect(mockUpdate.calledWith('')).toBeTruthy();
    });
});
