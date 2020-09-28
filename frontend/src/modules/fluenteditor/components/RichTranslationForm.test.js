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
    'message = Value\n    .attr-1 = And\n    .attr-2 = Attributes',
);

const EDITOR = {
    translation: TRANSLATION,
    errors: [],
    warnings: [],
};

describe('<RichTranslationForm>', () => {
    it('renders textarea for a value and each attribute', () => {
        const wrapper = shallow(
            <RichTranslationForm
                editor={EDITOR}
                locale={DEFAULT_LOCALE}
                updateTranslation={sinon.stub()}
            />,
        );

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

        const wrapper = shallow(
            <RichTranslationForm
                editor={editor}
                locale={DEFAULT_LOCALE}
                updateTranslation={sinon.stub()}
            />,
        );

        expect(wrapper.find('textarea')).toHaveLength(2);

        expect(wrapper.find('label').at(0).html()).toContain('variant');
        expect(wrapper.find('textarea').at(0).html()).toContain('Hello!');

        expect(wrapper.find('label').at(1).html()).toContain('another-variant');
        expect(wrapper.find('textarea').at(1).html()).toContain('World!');
    });

    it('renders select expression in attributes properly', () => {
        const input = `
my-entry =
    .label =
        { PLATFORM() ->
            [macosx] Preferences
           *[other] Options
        }
    .accesskey =
        { PLATFORM() ->
            [macosx] e
           *[other] s
        }`;

        const editor = {
            ...EDITOR,
            translation: fluent.parser.parseEntry(input),
        };

        const wrapper = shallow(
            <RichTranslationForm
                editor={editor}
                locale={DEFAULT_LOCALE}
                updateTranslation={sinon.stub()}
            />,
        );

        expect(wrapper.find('textarea')).toHaveLength(4);

        expect(wrapper.find('label .attribute-label').at(0).html()).toContain(
            'label',
        );
        expect(wrapper.find('label .label').at(0).html()).toContain('macosx');
        expect(wrapper.find('textarea').at(0).html()).toContain('Preferences');

        expect(wrapper.find('label .attribute-label').at(1).html()).toContain(
            'label',
        );
        expect(wrapper.find('label').at(1).html()).toContain('other');
        expect(wrapper.find('textarea').at(1).html()).toContain('Options');

        expect(wrapper.find('label .attribute-label').at(2).html()).toContain(
            'accesskey',
        );
        expect(wrapper.find('label').at(2).html()).toContain('macosx');
        expect(wrapper.find('textarea').at(2).html()).toContain('e');

        expect(wrapper.find('label .attribute-label').at(3).html()).toContain(
            'accesskey',
        );
        expect(wrapper.find('label').at(3).html()).toContain('other');
        expect(wrapper.find('textarea').at(3).html()).toContain('s');
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

        const wrapper = shallow(
            <RichTranslationForm
                editor={editor}
                locale={DEFAULT_LOCALE}
                updateTranslation={sinon.stub()}
            />,
        );

        expect(wrapper.find('textarea')).toHaveLength(2);

        expect(wrapper.find('textarea').at(0).html()).toContain('Hello!');

        const varsSingular = wrapper
            .find('#fluenteditor-RichTranslationForm--plural-example')
            .at(0)
            .prop('vars');
        expect(varsSingular.plural).toEqual('one');
        expect(varsSingular.example).toEqual(1);

        expect(wrapper.find('textarea').at(1).html()).toContain('World!');

        const varsPlural = wrapper
            .find('#fluenteditor-RichTranslationForm--plural-example')
            .at(1)
            .prop('vars');
        expect(varsPlural.plural).toEqual('other');
        expect(varsPlural.example).toEqual(2);
    });

    it('renders access keys properly', () => {
        const input = `
title = Title
    .label = Candidates
    .accesskey = C`;

        const editor = {
            ...EDITOR,
            translation: fluent.parser.parseEntry(input),
        };

        const wrapper = shallow(
            <RichTranslationForm
                editor={editor}
                locale={DEFAULT_LOCALE}
                updateTranslation={sinon.stub()}
            />,
        );

        expect(wrapper.find('textarea')).toHaveLength(3);

        expect(wrapper.find('label').at(1).html()).toContain('label');
        expect(wrapper.find('textarea').at(1).prop('value')).toEqual(
            'Candidates',
        );

        expect(wrapper.find('label').at(2).html()).toContain('accesskey');
        expect(wrapper.find('textarea').at(2).prop('value')).toEqual('C');
        expect(wrapper.find('textarea').at(2).prop('maxLength')).toEqual(1);

        expect(wrapper.find('.accesskeys')).toHaveLength(1);
        expect(wrapper.find('.accesskeys button')).toHaveLength(8);
        expect(wrapper.find('.accesskeys button').at(0).text()).toEqual('C');
        expect(wrapper.find('.accesskeys button').at(1).text()).toEqual('a');
        expect(wrapper.find('.accesskeys button').at(2).text()).toEqual('n');
        expect(wrapper.find('.accesskeys button').at(3).text()).toEqual('d');
        expect(wrapper.find('.accesskeys button').at(4).text()).toEqual('i');
        expect(wrapper.find('.accesskeys button').at(5).text()).toEqual('t');
        expect(wrapper.find('.accesskeys button').at(6).text()).toEqual('e');
        expect(wrapper.find('.accesskeys button').at(7).text()).toEqual('s');
    });

    it('does not render the access key UI if no candidates can be generated', () => {
        const input = `
title =
    .label = { reference }
    .accesskey = C`;

        const editor = {
            ...EDITOR,
            translation: fluent.parser.parseEntry(input),
        };

        const wrapper = shallow(
            <RichTranslationForm
                editor={editor}
                locale={DEFAULT_LOCALE}
                updateTranslation={sinon.stub()}
            />,
        );

        expect(wrapper.find('.accesskeys')).toHaveLength(0);
    });

    it('does not render the access key UI if access key is longer than 1 character', () => {
        const input = `
title =
    .label = Candidates
    .accesskey = { reference }`;

        const editor = {
            ...EDITOR,
            translation: fluent.parser.parseEntry(input),
        };

        const wrapper = shallow(
            <RichTranslationForm
                editor={editor}
                locale={DEFAULT_LOCALE}
                updateTranslation={sinon.stub()}
            />,
        );

        expect(wrapper.find('.accesskeys')).toHaveLength(0);
    });

    it('calls the updateTranslation function on mount and change', () => {
        const updateMock = sinon.spy();

        const wrapper = shallow(
            <RichTranslationForm
                editor={EDITOR}
                locale={DEFAULT_LOCALE}
                updateTranslation={updateMock}
            />,
        );

        expect(updateMock.calledOnce).toBeTruthy();
        wrapper
            .find('textarea')
            .at(0)
            .simulate('change', { currentTarget: { value: 'good bye' } });
        expect(updateMock.calledTwice).toBeTruthy();
    });

    it('updates the translation when selectionReplacementContent is passed', () => {
        const resetMock = sinon.stub();
        const updateMock = sinon.stub();

        const wrapper = mount(
            <RichTranslationForm
                editor={EDITOR}
                locale={DEFAULT_LOCALE}
                unsavedchanges={{ shown: false }}
                resetSelectionContent={resetMock}
                updateTranslation={updateMock}
                updateUnsavedChanges={sinon.stub()}
            />,
        );

        wrapper.setProps({
            editor: { ...EDITOR, selectionReplacementContent: 'hello ' },
        });

        const updatedTranslation = fluent.parser.parseEntry(
            'message = hello Value\n    .attr-1 = And\n    .attr-2 = Attributes',
        );

        expect(updateMock.calledTwice).toBeTruthy();
        expect(updateMock.calledWith(updatedTranslation)).toBeTruthy();
        expect(resetMock.calledOnce).toBeTruthy();
    });
});
