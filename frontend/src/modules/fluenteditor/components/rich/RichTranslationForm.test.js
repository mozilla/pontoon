import sinon from 'sinon';

import * as editor from 'core/editor';
import * as locale from 'core/locale';
import { fluent } from 'core/utils';

import { createReduxStore, mountComponentWithStore } from 'test/store';

import RichTranslationForm from './RichTranslationForm';

const DEFAULT_LOCALE = {
    direction: 'ltr',
    code: 'kg',
    script: 'Latin',
    cldrPlurals: [1, 5],
};

function createComponent(entityString, updateTranslation?) {
    if (!updateTranslation) {
        updateTranslation = sinon.fake();
    }

    const store = createReduxStore();
    store.dispatch(locale.actions.receive(DEFAULT_LOCALE));

    const message = fluent.parser.parseEntry(entityString);
    store.dispatch(editor.actions.update(message));
    store.dispatch(editor.actions.setInitialTranslation(message));

    const wrapper = mountComponentWithStore(RichTranslationForm, store, {
        updateTranslation,
    });

    wrapper.update();

    return [wrapper, store];
}

describe('<RichTranslationForm>', () => {
    it('renders textarea for a value and each attribute', () => {
        const [wrapper] = createComponent(
            `message = Value
    .attr-1 = And
    .attr-2 = Attributes
`,
        );

        expect(wrapper.find('textarea')).toHaveLength(3);
        expect(wrapper.find('textarea').at(0).html()).toContain('Value');
        expect(wrapper.find('textarea').at(1).html()).toContain('And');
        expect(wrapper.find('textarea').at(2).html()).toContain('Attributes');
    });

    it('renders select expression properly', () => {
        const [wrapper] = createComponent(
            `my-entry =
    { PLATFORM() ->
        [variant] Hello!
       *[another-variant] World!
    }
`,
        );

        expect(wrapper.find('textarea')).toHaveLength(2);

        expect(wrapper.find('label').at(0).html()).toContain('variant');
        expect(wrapper.find('textarea').at(0).html()).toContain('Hello!');

        expect(wrapper.find('label').at(1).html()).toContain('another-variant');
        expect(wrapper.find('textarea').at(1).html()).toContain('World!');
    });

    it('renders select expression in attributes properly', () => {
        const [wrapper] = createComponent(
            `my-entry =
    .label =
        { PLATFORM() ->
            [macosx] Preferences
           *[other] Options
        }
    .accesskey =
        { PLATFORM() ->
            [macosx] e
           *[other] s
        }
`,
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
        const [wrapper] = createComponent(
            `my-entry =
    { $num ->
        [one] Hello!
       *[other] World!
    }
`,
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
        const [wrapper] = createComponent(
            `title = Title
    .label = Candidates
    .accesskey = C
`,
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
        const [wrapper] = createComponent(
            `title =
    .label = { reference }
    .accesskey = C
`,
        );

        expect(wrapper.find('.accesskeys')).toHaveLength(0);
    });

    it('does not render the access key UI if access key is longer than 1 character', () => {
        const [wrapper] = createComponent(
            `title =
    .label = Candidates
    .accesskey = { reference }
`,
        );

        expect(wrapper.find('.accesskeys')).toHaveLength(0);
    });

    it('updates the translation when selectionReplacementContent is passed', async () => {
        const updateMock = sinon.spy();
        const [wrapper, store] = createComponent(
            `title = Value
    .label = Something
`,
            updateMock,
        );

        await store.dispatch(editor.actions.updateSelection('Add'));

        // Force a re-render -- see https://enzymejs.github.io/enzyme/docs/api/ReactWrapper/update.html
        wrapper.setProps({});

        expect(updateMock.called).toBeTruthy();
        const replaceContent = fluent.parser.parseEntry(
            `title = AddValue
    .label = Something
`,
        );
        expect(updateMock.calledWith(replaceContent)).toBeTruthy();
    });
});
