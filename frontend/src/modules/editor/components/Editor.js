/* @flow */

import * as React from 'react';
import { Localized } from 'fluent-react';

import './Editor.css';

import { PluralSelector } from 'core/plural';

import EditorProxy from './EditorProxy';
import EditorSettings from './EditorSettings';

import type { Locale } from 'core/locales';
import type { SettingsState } from 'core/user';
import type { DbEntity } from 'modules/entitieslist';


type Props = {|
    translation: string,
    entity: ?DbEntity,
    locale: Locale,
    pluralForm: number,
    settings: SettingsState,
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
                <EditorSettings
                    settings={ this.props.settings }
                    updateSetting={ this.props.updateSetting }
                />
                <div className="actions">
                    <Localized id="entitydetails-editor-button-copy">
                        <button
                            className="action-copy"
                            onClick={ this.copyOriginalIntoEditor }
                        >
                            Copy
                        </button>
                    </Localized>
                    <Localized id="entitydetails-editor-button-clear">
                        <button
                            className="action-clear"
                            onClick={ this.clearEditor }
                        >
                            Clear
                        </button>
                    </Localized>
                    { this.props.settings.forceSuggestions ?
                    // Suggest button, will send an unreviewed translation.
                    <Localized id="entitydetails-editor-button-suggest">
                        <button
                            className="action-suggest"
                            onClick={ this.sendTranslation }
                        >
                            Suggest
                        </button>
                    </Localized>
                    :
                    // Save button, will send an approved translation.
                    <Localized id="entitydetails-editor-button-save">
                        <button
                            className="action-save"
                            onClick={ this.sendTranslation }
                        >
                            Save
                        </button>
                    </Localized>
                    }
                </div>
                <div className="clearfix">
                </div>
            </menu>
        </div>;
    }
}
