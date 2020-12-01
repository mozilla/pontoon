import React from 'react';

import * as entities from 'core/entities';
import * as navigation from 'core/navigation';

import EditorMenu from './EditorMenu';
import EditorSettings from './EditorSettings';
import KeyboardShortcuts from './KeyboardShortcuts';
import TranslationLength from './TranslationLength';

import {
    createDefaultUser,
    createReduxStore,
    mountComponentWithStore,
} from 'test/store';

const SELECTED_ENTITY = {
    pk: 1,
    original: 'le test',
    original_plural: 'les tests',
    translation: [{ string: 'test' }, { string: 'test plural' }],
};

async function createEditorMenu({
    forceSuggestions = true,
    isAuthenticated = true,
    entity = SELECTED_ENTITY,
    firstItemHook = null,
} = {}) {
    const store = createReduxStore();
    createDefaultUser(store, {
        is_authenticated: isAuthenticated,
        settings: {
            force_suggestions: forceSuggestions,
        },
    });

    store.dispatch(entities.actions.receive([entity], false));

    const wrapper = mountComponentWithStore(EditorMenu, store, {
        firstItemHook,
    });

    await store.dispatch(
        navigation.actions.updateEntity(store.getState().router, 1),
    );

    return wrapper;
}

function expectHiddenSettingsAndActions(wrapper) {
    expect(wrapper.find('button')).toHaveLength(0);
    expect(wrapper.find(EditorSettings)).toHaveLength(0);
    expect(wrapper.find(KeyboardShortcuts)).toHaveLength(0);
    expect(wrapper.find(TranslationLength)).toHaveLength(0);
    expect(wrapper.find('#editor-EditorMenu--button-copy')).toHaveLength(0);
}

describe('<EditorMenu>', () => {
    it('renders correctly', async () => {
        const wrapper = await createEditorMenu();

        // 3 buttons to control the editor.
        expect(wrapper.find('.action-copy').exists()).toBeTruthy();
        expect(wrapper.find('.action-clear').exists()).toBeTruthy();
        expect(wrapper.find('EditorMainAction')).toHaveLength(1);
    });

    it('hides the settings and actions when the user is logged out', async () => {
        const wrapper = await createEditorMenu({ isAuthenticated: false });

        expectHiddenSettingsAndActions(wrapper);

        expect(
            wrapper.find('#editor-EditorMenu--sign-in-to-translate'),
        ).toHaveLength(1);
    });

    it('hides the settings and actions when the entity is read-only', async () => {
        const entity = {
            ...SELECTED_ENTITY,
            readonly: true,
        };
        const wrapper = await createEditorMenu({ entity });

        expectHiddenSettingsAndActions(wrapper);

        expect(
            wrapper.find('#editor-EditorMenu--read-only-localization'),
        ).toHaveLength(1);
    });

    it('accepts a firstItemHook and shows it as its first child', async () => {
        const firstItemHook = <p>Hello</p>;
        const wrapper = await createEditorMenu({ firstItemHook });

        expect(wrapper.find('menu').children().first().text()).toEqual('Hello');
    });
});
