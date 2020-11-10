import * as editor from 'core/editor';
import * as entities from 'core/entities';
import * as navigation from 'core/navigation';

import {
    createDefaultUser,
    createReduxStore,
    mountComponentWithStore,
} from 'test/store';

import FluentEditor from './FluentEditor';

const NESTED_SELECTORS_STRING = `my-message =
    { $thing ->
        *[option] { $stuff ->
            [foo] FOO
            *[bar] BAR
        }
        [select] WOW
    }
`;

const RICH_MESSAGE_STRING = `my-message =
    Why so serious?
    .reason = Because
`;

const ENTITIES = [
    {
        pk: 1,
        original: 'my-message = Hello',
        translation: [
            {
                string: 'my-message = Salut',
            },
        ],
    },
    {
        pk: 2,
        original: 'my-message =\n    .my-attr = Something guud',
        translation: [
            { string: 'my-message =\n    .my-attr = Quelque chose de bien' },
        ],
    },
    {
        pk: 3,
        original: NESTED_SELECTORS_STRING,
        translation: [{ string: NESTED_SELECTORS_STRING }],
    },
    {
        pk: 4,
        original: 'my-message = Hello',
        translation: [{ string: '' }],
    },
    {
        pk: 5,
        original: RICH_MESSAGE_STRING,
        translation: [],
    },
];

async function createComponent(entityPk = 0) {
    const store = createReduxStore();
    createDefaultUser(store);

    const wrapper = mountComponentWithStore(FluentEditor, store);

    store.dispatch(entities.actions.receive(ENTITIES));
    await store.dispatch(
        navigation.actions.updateEntity(store.getState().router, entityPk),
    );

    wrapper.update();

    return [wrapper, store];
}

describe('<FluentEditor>', () => {
    it('renders the simple form when passing a simple string', async () => {
        const [wrapper] = await createComponent(1);

        expect(wrapper.find('SourceEditor').exists()).toBeFalsy();
        expect(wrapper.find('SimpleEditor').exists()).toBeTruthy();
    });

    it('renders the simple form when passing a simple string with one attribute', async () => {
        const [wrapper] = await createComponent(2);

        expect(wrapper.find('SourceEditor').exists()).toBeFalsy();
        expect(wrapper.find('SimpleEditor').exists()).toBeTruthy();
    });

    it('renders the rich form when passing a supported rich message', async () => {
        const [wrapper] = await createComponent(5);

        expect(wrapper.find('RichEditor').exists()).toBeTruthy();
    });

    it('renders the source form when passing a complex string', async () => {
        const [wrapper] = await createComponent(3);

        expect(wrapper.find('SourceEditor').exists()).toBeTruthy();
        expect(wrapper.find('SimpleEditor').exists()).toBeFalsy();
    });

    it('converts translation when switching source mode', async () => {
        const [wrapper] = await createComponent(1);
        expect(wrapper.find('SimpleEditor').exists()).toBeTruthy();

        // Force source mode.
        wrapper.find('button.ftl').simulate('click');

        expect(wrapper.find('SourceEditor').exists()).toBeTruthy();
        expect(wrapper.find('textarea').text()).toEqual('my-message = Salut\n');
    });

    it('sets empty initial translation in source mode when untranslated', async () => {
        const [wrapper] = await createComponent(4);

        // Force source mode.
        wrapper.find('button.ftl').simulate('click');

        expect(wrapper.find('SourceEditor').exists()).toBeTruthy();
        expect(wrapper.find('textarea').text()).toEqual('my-message = ');
    });

    it('changes editor implementation when changing translation syntax', async () => {
        const [wrapper, store] = await createComponent(1);
        expect(wrapper.find('SimpleEditor').exists()).toBeTruthy();

        // Change translation to a rich string.
        store.dispatch(editor.actions.update(RICH_MESSAGE_STRING, 'external'));
        wrapper.update();

        expect(wrapper.find('RichEditor').exists()).toBeTruthy();
    });
});
