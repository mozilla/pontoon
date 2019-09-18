import React from 'react';
import { mount, shallow } from 'enzyme';
import sinon from 'sinon';

import { fluent } from 'core/utils';

import RichTranslationForm from './RichTranslationForm';


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


describe('<RichTranslationForm>', () => {
    it('renders textarea for a value and each attribute', () => {
        const wrapper = shallow(<RichTranslationForm
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

        const wrapper = shallow(<RichTranslationForm
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

        const wrapper = shallow(<RichTranslationForm
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

        const wrapper = shallow(<RichTranslationForm
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

        const wrapper = mount(<RichTranslationForm
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
});
