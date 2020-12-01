import * as editor from 'core/editor';
import * as entities from 'core/entities';
import * as navigation from 'core/navigation';
import * as plural from 'core/plural';

import {
    createDefaultUser,
    createReduxStore,
    mountComponentWithStore,
} from 'test/store';

import GenericEditor from './GenericEditor';

const ENTITIES = [
    {
        pk: 1,
        original: 'something',
        translation: [
            {
                string: 'quelque chose',
            },
        ],
    },
    {
        pk: 2,
        original: 'second',
        original_plural: 'seconds',
        translation: [{ string: 'deuxième' }, { string: 'deuxièmes' }],
    },
];

async function createComponent(entityIndex = 0) {
    const store = createReduxStore();
    createDefaultUser(store);

    const wrapper = mountComponentWithStore(GenericEditor, store);

    store.dispatch(entities.actions.receive(ENTITIES));
    await store.dispatch(
        navigation.actions.updateEntity(store.getState().router, entityIndex),
    );

    // Force a re-render.
    wrapper.setProps({});

    return [wrapper, store];
}

describe('<Editor>', () => {
    it('updates translation on mount', async () => {
        const [, store] = await createComponent(1);
        expect(store.getState().editor.translation).toEqual('quelque chose');
    });

    it('sets initial translation on mount', async () => {
        const [, store] = await createComponent(1);
        expect(store.getState().editor.initialTranslation).toEqual(
            'quelque chose',
        );
    });

    it('updates translation when entity or plural change', async () => {
        const [wrapper, store] = await createComponent(1);

        await store.dispatch(
            navigation.actions.updateEntity(store.getState().router, 2),
        );
        expect(store.getState().editor.translation).toEqual('deuxième');

        await store.dispatch(plural.actions.select(1));
        wrapper.setProps({});
        expect(store.getState().editor.translation).toEqual('deuxièmes');
    });

    it('sets initial translation when entity or plural change', async () => {
        const [wrapper, store] = await createComponent(1);

        await store.dispatch(
            navigation.actions.updateEntity(store.getState().router, 2),
        );
        expect(store.getState().editor.initialTranslation).toEqual('deuxième');

        await store.dispatch(plural.actions.select(1));
        wrapper.setProps({});
        expect(store.getState().editor.initialTranslation).toEqual('deuxièmes');
    });

    it('does not set initial translation when translation changes', async () => {
        const [, store] = await createComponent(1);
        expect(store.getState().editor.initialTranslation).toEqual(
            'quelque chose',
        );

        store.dispatch(editor.actions.update('autre chose'));
        expect(store.getState().editor.initialTranslation).toEqual(
            'quelque chose',
        );
    });
});
