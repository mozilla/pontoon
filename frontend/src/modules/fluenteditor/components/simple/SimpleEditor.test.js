import sinon from 'sinon';

import * as editor from 'core/editor';
import * as entities from 'core/entities';
import * as navigation from 'core/navigation';
import { fluent } from 'core/utils';

import { createReduxStore, mountComponentWithStore } from 'test/store';

import SimpleEditor from './SimpleEditor';

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
];

async function createSimpleEditor(entityIndex = 1) {
    const store = createReduxStore();
    const wrapper = mountComponentWithStore(SimpleEditor, store, {
        ftlSwitch: null,
    });

    store.dispatch(entities.actions.receive(ENTITIES));
    await store.dispatch(
        navigation.actions.updateEntity(store.getState().router, entityIndex),
    );

    wrapper.update();

    return [wrapper, store];
}

describe('<SimpleEditor>', () => {
    it('parses content that comes from an external source', async () => {
        const [wrapper, store] = await createSimpleEditor();

        // Update the content with a non-formatted Fluent string.
        await store.dispatch(
            editor.actions.update('my-message = Coucou', 'external'),
        );

        // Force a re-render -- see https://enzymejs.github.io/enzyme/docs/api/ReactWrapper/update.html
        wrapper.setProps({});

        // The translation has been updated to a simplified preview.
        expect(wrapper.find('textarea').text()).toEqual('Coucou');
    });

    it('does not render when translation is not a string', async () => {
        const [wrapper, store] = await createSimpleEditor();

        // Update the content with a non-formatted Fluent string.
        store.dispatch(
            editor.actions.update(fluent.parser.parseEntry('hello = World')),
        );
        wrapper.update();

        expect(wrapper.isEmptyRender()).toBeTruthy();
    });

    it('passes a reconstructed translation to sendTranslation', async () => {
        const sendTranslationMock = sinon.stub(
            editor.actions,
            'sendTranslation',
        );
        sendTranslationMock.returns({ type: 'whatever' });

        const [wrapper, store] = await createSimpleEditor();

        store.dispatch(editor.actions.update('Coucou'));
        wrapper.update();

        // Intercept the sendTranslation prop and call it directly.
        wrapper.find('GenericTranslationForm').prop('sendTranslation')();

        expect(sendTranslationMock.calledOnce).toBeTruthy();
        expect(sendTranslationMock.lastCall.args[1]).toEqual(
            'my-message = Coucou\n',
        );

        sendTranslationMock.restore();
    });
});
