/* @flow */

import * as React from 'react';
import { Localized } from 'fluent-react';

import './Editor.css';

import { PluralSelector } from 'core/plural';
import { SignInLink } from 'core/user';

import EditorProxy from './EditorProxy';
import EditorSettings from './EditorSettings';
import KeyboardShortcuts from './KeyboardShortcuts';

import type { Locale } from 'core/locales';
import type { UserState } from 'core/user';
import type { DbEntity } from 'modules/entitieslist';


type Props = {|
    translation: string,
    entity: ?DbEntity,
    locale: Locale,
    pluralForm: number,
    user: UserState,
    sendTranslation: () => void,
    updateEditorTranslation: (string) => void,
    updateSetting: (string, boolean) => void,
|};

type State = {|
    translation: string,
|};


/**
 * Editor for translation strings.
 *
 * Will present a different editor depending on the file format of the string,
 * see `EditorProxy` for more information.
 */
export default class Editor extends React.Component<Props, State> {
    componentDidUpdate(prevProps: Props) {
        if (this.props.translation !== prevProps.translation) {
            this.updateTranslation(this.props.translation);
        }
    }

    updateTranslation = (translation: string) => {
        this.props.updateEditorTranslation(translation);
    }

    copyOriginalIntoEditor = () => {
        const { entity, pluralForm } = this.props;
        if (entity) {
            if (pluralForm === -1 || pluralForm === 1) {
                this.updateTranslation(entity.original);
            }
            else {
                this.updateTranslation(entity.original_plural);
            }
        }
    }

    clearEditor = () => {
        this.updateTranslation('');
    }

    sendTranslation = () => {
        this.props.sendTranslation();
    }

    render() {
        return <div className="editor">
            <PluralSelector />
            <EditorProxy
                entity={ this.props.entity }
                translation={ this.props.translation }
                locale={ this.props.locale }
                updateTranslation={ this.updateTranslation }
            />
            <menu>
            { !this.props.user.isAuthenticated ?
                <Localized
                    id="editor-editor-sign-in-to-translate"
                    a={
                        <SignInLink></SignInLink>
                    }
                >
                    <p className='banner'>
                        { '<a>Sign in</a> to translate.' }
                    </p>
                </Localized>
            :
            <React.Fragment>
                <EditorSettings
                    settings={ this.props.user.settings }
                    updateSetting={ this.props.updateSetting }
                />
                <KeyboardShortcuts />
                <div className="actions">
                    <Localized id="editor-editor-button-copy">
                        <button
                            className="action-copy"
                            onClick={ this.copyOriginalIntoEditor }
                        >
                            Copy
                        </button>
                    </Localized>
                    <Localized id="editor-editor-button-clear">
                        <button
                            className="action-clear"
                            onClick={ this.clearEditor }
                        >
                            Clear
                        </button>
                    </Localized>
                    { this.props.user.settings.forceSuggestions ?
                    // Suggest button, will send an unreviewed translation.
                    <Localized id="editor-editor-button-suggest">
                        <button
                            className="action-suggest"
                            onClick={ this.sendTranslation }
                        >
                            Suggest
                        </button>
                    </Localized>
                    :
                    // Save button, will send an approved translation.
                    <Localized id="editor-editor-button-save">
                        <button
                            className="action-save"
                            onClick={ this.sendTranslation }
                        >
                            Save
                        </button>
                    </Localized>
                    }
                </div>
                <div className="clearfix" />
            </React.Fragment>
            }
            </menu>
        </div>;
    }
}
