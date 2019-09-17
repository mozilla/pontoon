import React from 'react';
import { mount, shallow } from 'enzyme';
import sinon from 'sinon';

import { fluent } from 'core/utils';

import { RichTranslationFormBase } from './RichTranslationForm';


const DEFAULT_LOCALE = {
    direction: 'ltr',
    code: 'kg',
    script: 'Latin',
    cldrPlurals: [1, 5],
};

const TRANSLATION = fluent.parser.parseEntry(
    'message = Value\n    .attr-1 = And\n    .attr-2 = Attributes'
)

const EDITOR = {
    translation: TRANSLATION,
    errors: [],
    warnings: [],
};


describe('<RichTranslationFormBase>', () => {
    it('renders textarea for a value and each attribute', () => {
        const wrapper = shallow(<RichTranslationFormBase
            editor={ EDITOR }
            locale={ DEFAULT_LOCALE }
            updateTranslation={ sinon.stub() }
        />);

        expect(wrapper.find('textarea')).toHaveLength(3);
        expect(wrapper.find('textarea').at(0).html()).toContain('Value');
        expect(wrapper.find('textarea').at(1).html()).toContain('And');
        expect(wrapper.find('textarea').at(2).html()).toContain('Attributes');
    });

    it('renders select expression properly', () => {
        const input = `
my-entry =
    { PLATFORM() ->
        [variant] Hello!
       *[another-variant] World!
    }`;

        const editor = {
            ...EDITOR,
            translation: fluent.parser.parseEntry(input),
        };

        const wrapper = shallow(<RichTranslationFormBase
            editor={ editor }
            locale={ DEFAULT_LOCALE }
            updateTranslation={ sinon.stub() }
        />);

        expect(wrapper.find('textarea')).toHaveLength(2);
        expect(wrapper.find('label').at(0).html()).toContain('variant');
        expect(wrapper.find('textarea').at(0).html()).toContain('Hello!');
        expect(wrapper.find('label').at(1).html()).toContain('another-variant');
        expect(wrapper.find('textarea').at(1).html()).toContain('World!');
    });

    it('renders plural string properly', () => {
        const input = `
my-entry =
    { $num ->
        [one] Hello!
       *[other] World!
    }`;

        const editor = {
            ...EDITOR,
            translation: fluent.parser.parseEntry(input),
        };

        const wrapper = shallow(<RichTranslationFormBase
            editor={ editor }
            locale={ DEFAULT_LOCALE }
            updateTranslation={ sinon.stub() }
        />);

        expect(wrapper.find('textarea')).toHaveLength(2);
        expect(wrapper.find('textarea').at(0).html()).toContain('Hello!');
        expect(wrapper.find('#fluenteditor-RichTranslationForm--plural-example').at(0).prop('$plural')).toEqual('one');
        expect(wrapper.find('#fluenteditor-RichTranslationForm--plural-example').at(0).prop('$example')).toEqual(1);
        expect(wrapper.find('textarea').at(1).html()).toContain('World!');
        expect(wrapper.find('#fluenteditor-RichTranslationForm--plural-example').at(1).prop('$plural')).toEqual('other');
        expect(wrapper.find('#fluenteditor-RichTranslationForm--plural-example').at(1).prop('$example')).toEqual(2);
    });

    it('calls the updateTranslation function on mount and change', () => {
        const updateMock = sinon.spy();

        const wrapper = shallow(<RichTranslationFormBase
            editor={ EDITOR }
            locale={ DEFAULT_LOCALE }
            updateTranslation={ updateMock }
        />);

        expect(updateMock.calledOnce).toBeTruthy();
        wrapper.find('textarea').at(0).simulate('change', { currentTarget: { value: 'good bye' } });
        expect(updateMock.calledTwice).toBeTruthy();
    });

    it('updates the translation when selectionReplacementContent is passed', () => {
        const resetMock = sinon.stub();
        const updateMock = sinon.stub();

        const wrapper = mount(<RichTranslationFormBase
            editor={ EDITOR }
            locale={ DEFAULT_LOCALE }
            unsavedchanges={ { shown: false } }
            resetSelectionContent={ resetMock }
            updateTranslation={ updateMock }
            updateUnsavedChanges={ sinon.stub() }
        />);

        wrapper.setProps({ editor: { ...EDITOR, selectionReplacementContent: 'hello ' } });

        const updatedTranslation = fluent.parser.parseEntry(
            'message = hello Value\n    .attr-1 = And\n    .attr-2 = Attributes'
        )

        expect(updateMock.calledTwice).toBeTruthy();
        expect(updateMock.calledWith(updatedTranslation)).toBeTruthy();
        expect(resetMock.calledOnce).toBeTruthy();
    });

    it('sends the translation on Enter', () => {
        const mockSend = sinon.spy();
        const wrapper = shallow(<RichTranslationFormBase
            editor={ EDITOR }
            locale={ DEFAULT_LOCALE }
            sendTranslation={ mockSend }
            disableAction={ sinon.spy() }
            unsavedchanges={ { shown: false } }
            updateTranslation={ sinon.stub() }
        />);

        const event = {
            preventDefault: sinon.spy(),
            keyCode: 13,  // Enter
            altKey: false,
            ctrlKey: false,
            shiftKey: false,
        };

        expect(mockSend.calledOnce).toBeFalsy();
        wrapper.find('textarea').at(0).simulate('keydown', event);
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

        const wrapper = shallow(<RichTranslationFormBase
            editor={ editor }
            locale={ DEFAULT_LOCALE }
            updateTranslation={ sinon.stub() }
            updateTranslationStatus={ mockSend }
            disableAction={ sinon.spy() }
            unsavedchanges={ { shown: false } }
        />);

        const event = {
            preventDefault: sinon.spy(),
            keyCode: 13,  // Enter
            altKey: false,
            ctrlKey: false,
            shiftKey: false,
        };

        expect(mockSend.calledOnce).toBeFalsy();
        wrapper.find('textarea').at(0).simulate('keydown', event);
        expect(mockSend.calledOnce).toBeTruthy();
    });

    it('ignores unsaved changes on Enter if unsaved changes popup is shown', () => {
        const mockSend = sinon.spy();
        const wrapper = shallow(<RichTranslationFormBase
            editor={ EDITOR }
            locale={ DEFAULT_LOCALE }
            ignoreUnsavedChanges={ mockSend }
            disableAction={ sinon.spy() }
            unsavedchanges={ { shown: true } }
            updateTranslation={ sinon.stub() }
        />);

        const event = {
            preventDefault: sinon.spy(),
            keyCode: 13,  // Enter
            altKey: false,
            ctrlKey: false,
            shiftKey: false,
        };

        expect(mockSend.calledOnce).toBeFalsy();
        wrapper.find('textarea').at(0).simulate('keydown', event);
        expect(mockSend.calledOnce).toBeTruthy();
    });

    it('closes unsaved changes popup if open on Esc', () => {
        const mockSend = sinon.spy();

        const wrapper = shallow(<RichTranslationFormBase
            editor={ EDITOR }
            locale={ DEFAULT_LOCALE }
            hideUnsavedChanges={ mockSend }
            unsavedchanges={ { shown: true } }
            updateTranslation={ sinon.stub() }
        />);

        const event = {
            preventDefault: sinon.spy(),
            keyCode: 27,  // Esc
        };

        expect(mockSend.calledOnce).toBeFalsy();
        wrapper.find('textarea').at(0).simulate('keydown', event);
        expect(mockSend.calledOnce).toBeTruthy();
    });

    it('closes failed checks popup if open on Esc', () => {
        const mockSend = sinon.spy();

        const editor = {
            ...EDITOR,
            errors: ['error1'],
            warnings: ['warning1'],
        }

        const wrapper = shallow(<RichTranslationFormBase
            editor={ editor }
            locale={ DEFAULT_LOCALE }
            resetFailedChecks={ mockSend }
            unsavedchanges={ { shown: false } }
            updateTranslation={ sinon.stub() }
        />);

        const event = {
            preventDefault: sinon.spy(),
            keyCode: 27,  // Esc
        };

        expect(mockSend.calledOnce).toBeFalsy();
        wrapper.find('textarea').at(0).simulate('keydown', event);
        expect(mockSend.calledOnce).toBeTruthy();
    });

    it('copies the original into the Editor on Ctrl + Shift + C', () => {
        const mockCopy = sinon.spy();
        const wrapper = shallow(<RichTranslationFormBase
            editor={ EDITOR }
            locale={ DEFAULT_LOCALE }
            copyOriginalIntoEditor={ mockCopy }
            updateTranslation={ sinon.stub() }
        />);

        const event = {
            preventDefault: sinon.spy(),
            keyCode: 67,  // C
            altKey: false,
            ctrlKey: true,
            shiftKey: true,
        };

        expect(mockCopy.calledOnce).toBeFalsy();
        wrapper.find('textarea').at(0).simulate('keydown', event);
        expect(mockCopy.calledOnce).toBeTruthy();
    });

    it('clears the translation on Ctrl + Shift + Backspace', () => {
        const clearMock = sinon.spy();
        const wrapper = shallow(<RichTranslationFormBase
            editor={ EDITOR }
            locale={ DEFAULT_LOCALE }
            clearEditor={ clearMock }
            updateTranslation={ sinon.stub() }
        />);

        const event = {
            preventDefault: sinon.spy(),
            keyCode: 8,  // Backspace
            altKey: false,
            ctrlKey: true,
            shiftKey: true,
        };

        expect(clearMock.calledOnce).toBeFalsy();
        wrapper.find('textarea').at(0).simulate('keydown', event);
        expect(clearMock.calledOnce).toBeTruthy();
    });
});
