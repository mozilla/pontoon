/* @flow */

import * as React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Localized } from '@fluent/react';

import './EditorMenu.css';

import * as entities from 'core/entities';
import * as user from 'core/user';
import * as unsavedchanges from 'modules/unsavedchanges';

import EditorMainAction from './EditorMainAction';
import EditorSettings from './EditorSettings';
import FailedChecks from './FailedChecks';
import KeyboardShortcuts from './KeyboardShortcuts';

type Props = {|
    firstItemHook?: React.Node,
    translationLengthHook?: React.Node,
    clearEditor: () => void,
    copyOriginalIntoEditor: () => void,
    sendTranslation: (ignoreWarnings?: boolean) => void,
|};

/**
 * Shows a menu bar used to control the Editor.
 *
 * If the user is not authenticated, shows a login button.
 * If the entity is read-only, shows a read-only notification.
 * Otherise, shows the various tools to control the editor.
 */
export default function EditorMenu(props: Props) {
    return (
        <menu className='editor-menu'>
            {props.firstItemHook}
            <FailedChecks sendTranslation={props.sendTranslation} />
            <unsavedchanges.UnsavedChanges />
            <MenuContent {...props} />
        </menu>
    );
}

function MenuContent(props: Props) {
    const dispatch = useDispatch();
    const entity = useSelector((state) =>
        entities.selectors.getSelectedEntity(state),
    );
    const userState = useSelector((state) => state.user);

    if (!userState.isAuthenticated) {
        return (
            <Localized
                id='editor-EditorMenu--sign-in-to-translate'
                elems={{ a: <user.SignInLink url={userState.signInURL} /> }}
            >
                <p className='banner'>{'<a>Sign in</a> to translate.'}</p>
            </Localized>
        );
    }

    if (entity && entity.readonly) {
        return (
            <Localized id='editor-EditorMenu--read-only-localization'>
                <p className='banner'>This is a read-only localization.</p>
            </Localized>
        );
    }

    function updateSetting(setting: string, value: boolean) {
        dispatch(user.actions.saveSetting(setting, value, userState.username));
    }

    return (
        <>
            <EditorSettings
                settings={userState.settings}
                updateSetting={updateSetting}
            />
            <KeyboardShortcuts />
            {props.translationLengthHook}
            <div className='actions'>
                <Localized
                    id='editor-EditorMenu--button-copy'
                    attrs={{ title: true }}
                >
                    <button
                        className='action-copy'
                        onClick={props.copyOriginalIntoEditor}
                        title='Copy From Source (Ctrl + Shift + C)'
                    >
                        Copy
                    </button>
                </Localized>
                <Localized
                    id='editor-EditorMenu--button-clear'
                    attrs={{ title: true }}
                >
                    <button
                        className='action-clear'
                        onClick={props.clearEditor}
                        title='Clear Translation (Ctrl + Shift + Backspace)'
                    >
                        Clear
                    </button>
                </Localized>
                <EditorMainAction sendTranslation={props.sendTranslation} />
            </div>
        </>
    );
}
