import React from 'react';
import { shallow } from 'enzyme';

import EditorMenu from './EditorMenu';
import EditorSettings from './EditorSettings';
import KeyboardShortcuts from './KeyboardShortcuts';
import TranslationLength from './TranslationLength';

const LOCALE = {
    code: 'kg',
};

const SELECTED_ENTITY = {
    pk: 42,
    original: 'le test',
    original_plural: 'les tests',
    translation: [{ string: 'test' }, { string: 'test plural' }],
};

function createEditorMenu({
    forceSuggestions = true,
    isAuthenticated = true,
    entity = SELECTED_ENTITY,
    firstItemHook = null,
} = {}) {
    return shallow(
        <EditorMenu
            editor={{ translation: 'initial' }}
            locale={LOCALE}
            parameters={{ resource: 'resource' }}
            entity={entity}
            user={{
                isAuthenticated,
                username: 'Sarevok',
                settings: {
                    forceSuggestions,
                },
            }}
            firstItemHook={firstItemHook}
        />,
    );
}

function expectHiddenSettingsAndActions(wrapper) {
    expect(wrapper.find('button')).toHaveLength(0);
    expect(wrapper.find(EditorSettings)).toHaveLength(0);
    expect(wrapper.find(KeyboardShortcuts)).toHaveLength(0);
    expect(wrapper.find(TranslationLength)).toHaveLength(0);
    expect(wrapper.find('#editor-EditorMenu--button-copy')).toHaveLength(0);
}

describe('<EditorMenu>', () => {
    it('renders correctly', () => {
        const wrapper = createEditorMenu();

        // 3 buttons to control the editor.
        expect(wrapper.find('button')).toHaveLength(2);
        expect(wrapper.find('EditorMainAction')).toHaveLength(1);
    });

    it('hides the settings and actions when the user is logged out', () => {
        const wrapper = createEditorMenu({ isAuthenticated: false });

        expectHiddenSettingsAndActions(wrapper);

        expect(
            wrapper.find('#editor-EditorMenu--sign-in-to-translate'),
        ).toHaveLength(1);
    });

    it('hides the settings and actions when the entity is read-only', () => {
        const entity = {
            ...SELECTED_ENTITY,
            readonly: true,
        };
        const wrapper = createEditorMenu({ entity });

        expectHiddenSettingsAndActions(wrapper);

        expect(
            wrapper.find('#editor-EditorMenu--read-only-localization'),
        ).toHaveLength(1);
    });

    it('accepts a firstItemHook and shows it as its first child', () => {
        const firstItemHook = <p>Hello</p>;
        const wrapper = createEditorMenu({ firstItemHook });

        expect(wrapper.find('menu').children().first().text()).toEqual('Hello');
    });
});
