/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

import './EditorMenu.css';

import * as editor from 'core/editor';
import * as user from 'core/user';
import * as unsavedchanges from 'modules/unsavedchanges';

import type { EditorProps } from 'core/editor';


type Props = {
    ...EditorProps,
    firstItemHook?: React.Node,
    translationLengthHook?: React.Node,
};

/**
 * Render the options to control an Editor.
 */
export default class EditorMenu extends React.Component<Props> {
    render() {
        const props = this.props;

        return <menu className='editor-menu'>
            { props.firstItemHook }
            <editor.FailedChecks
                source={ props.editor.source }
                user={ props.user }
                errors={ props.editor.errors }
                warnings={ props.editor.warnings }
                resetFailedChecks={ props.resetFailedChecks }
                sendTranslation={ props.sendTranslation }
                updateTranslationStatus={ props.updateTranslationStatus }
            />
            <unsavedchanges.UnsavedChanges />
            { !props.user.isAuthenticated ?
                <Localized
                    id="editor-EditorMenu--sign-in-to-translate"
                    a={
                        <user.SignInLink url={ props.user.signInURL }></user.SignInLink>
                    }
                >
                    <p className='banner'>
                        { '<a>Sign in</a> to translate.' }
                    </p>
                </Localized>
            : (props.entity && props.entity.readonly) ?
                <Localized
                    id="editor-EditorMenu--read-only-localization"
                >
                    <p className='banner'>This is a read-only localization.</p>
                </Localized>
            :
                <React.Fragment>
                    <editor.EditorSettings
                        settings={ props.user.settings }
                        updateSetting={ props.updateSetting }
                    />
                    <editor.KeyboardShortcuts />
                    { props.translationLengthHook }
                    <div className="actions">
                        <Localized
                            id="editor-EditorMenu--button-copy"
                            attrs={{ title: true }}
                        >
                            <button
                                className="action-copy"
                                onClick={ props.copyOriginalIntoEditor }
                                title="Copy From Source (Ctrl + Shift + C)"
                            >
                                Copy
                            </button>
                        </Localized>
                        <Localized
                            id="editor-EditorMenu--button-clear"
                            attrs={{ title: true }}
                        >
                            <button
                                className="action-clear"
                                onClick={ props.clearEditor }
                                title="Clear Translation (Ctrl + Shift + Backspace)"
                            >
                                Clear
                            </button>
                        </Localized>
                        { props.user.settings.forceSuggestions ?
                        // Suggest button, will send an unreviewed translation.
                        <Localized
                            id="editor-EditorMenu--button-suggest"
                            attrs={{ title: true }}
                        >
                            <button
                                className="action-suggest"
                                onClick={ props.sendTranslation }
                                title="Suggest Translation (Enter)"
                            >
                                Suggest
                            </button>
                        </Localized>
                        :
                        // Save button, will send an approved translation.
                        <Localized
                            id="editor-EditorMenu--button-save"
                            attrs={{ title: true }}
                        >
                            <button
                                className="action-save"
                                onClick={ props.sendTranslation }
                                title="Save Translation (Enter)"
                            >
                                Save
                            </button>
                        </Localized>
                        }
                    </div>
                </React.Fragment>
            }
        </menu>;
    }
}
