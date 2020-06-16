/* @flow */

import React from 'react';
import { Localized } from '@fluent/react';

import './Translation.css';

import { GenericTranslation } from 'core/translation';

import TranslationSource from './TranslationSource';

import type { EditorState } from 'core/editor';
import type { MachineryTranslation, SourceType } from 'core/api';
import type { Locale } from 'core/locale';


type Props = {|
    editor: EditorState,
    isReadOnlyEditor: boolean,
    locale: Locale,
    sourceString: string,
    translation: MachineryTranslation,
    addTextToEditorTranslation: (string, ?string) => void,
    updateEditorTranslation: (string, string) => void,
    updateMachinerySources: (Array<SourceType>, string) => void,
|};


/**
 * Render a Translation in the Machinery tab.
 *
 * Shows the original string and the translation, as well as a list of sources.
 * Similar translations (same original and translation) are shown only once
 * and their sources are merged.
 */
export default class Translation extends React.Component<Props> {
    copyTranslationIntoEditor = () => {
        if (this.props.isReadOnlyEditor) {
            return;
        }

        // Ignore if selecting text
        if (window.getSelection().toString()) {
            return;
        }

        const { translation, sources } = this.props.translation;
        if (typeof(this.props.editor.translation) !== 'string') {
            // This is a Fluent Message, thus we are in the RichEditor.
            // Handle machinery differently.
            this.props.addTextToEditorTranslation(translation, 'machinery');
        }
        else {
            this.props.updateEditorTranslation(translation, 'machinery');
        }
        this.props.updateMachinerySources(sources, translation);
    };

    render() {
        const { locale, sourceString, translation, isReadOnlyEditor } = this.props;

        const types = translation.sources;

        let className = 'translation';

        if (isReadOnlyEditor) {
            // Copying into the editor is not allowed
            className += ' cannot-copy';
        }

        return <Localized id="machinery-Translation--copy" attrs={{ title: true }}>
            <li
                className={ className }
                title="Copy Into Translation"
                onClick={ this.copyTranslationIntoEditor }
            >
                <header>
                    { !translation.quality ? null :
                        <span className="quality">{ translation.quality + '%' }</span>
                    }
                    <TranslationSource
                        translation={ translation }
                        locale={ locale }
                    />
                </header>
                <p className="original">
                    { types.indexOf('caighdean') === -1 ?
                        <GenericTranslation
                            content={ translation.original }
                            diffTarget={ sourceString }
                        />
                    :
                        /*
                         * Caighdean takes `gd` translations as input, so we shouldn't
                         * diff it against the `en-US` source string.
                         */
                         <GenericTranslation
                             content= { translation.original }
                         />
                    }
                </p>
                <p
                    className="suggestion"
                    dir={ locale.direction }
                    data-script={ locale.script }
                    lang={ locale.code }
                >
                    <GenericTranslation
                        content={ translation.translation }
                    />
                </p>
            </li>
        </Localized>;
    }
}
