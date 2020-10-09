/* @flow */

import * as React from 'react';
import { useSelector } from 'react-redux';
import { Localized } from '@fluent/react';

import './Translation.css';

import * as entities from 'core/entities';
import { GenericTranslation } from 'core/translation';

import TranslationSource from './TranslationSource';

import type { MachineryTranslation, SourceType } from 'core/api';

type Props = {|
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
export default function Translation(props: Props) {
    const {
        addTextToEditorTranslation,
        updateEditorTranslation,
        updateMachinerySources,
        sourceString,
        translation,
    } = props;

    const editorContent = useSelector((state) => state.editor.translation);
    const isReadOnlyEditor = useSelector((state) =>
        entities.selectors.isReadOnlyEditor(state),
    );
    const locale = useSelector((state) => state.locale);

    const copyTranslationIntoEditor = React.useCallback(() => {
        if (isReadOnlyEditor) {
            return;
        }

        // Ignore if selecting text
        if (window.getSelection().toString()) {
            return;
        }

        if (typeof editorContent !== 'string') {
            // This is a Fluent Message, thus we are in the RichEditor.
            // Handle machinery differently.
            addTextToEditorTranslation(translation.translation, 'machinery');
        } else {
            updateEditorTranslation(translation.translation, 'machinery');
        }
        updateMachinerySources(translation.sources, translation.translation);
    }, [
        isReadOnlyEditor,
        translation,
        editorContent,
        addTextToEditorTranslation,
        updateEditorTranslation,
        updateMachinerySources,
    ]);

    let className = 'translation';
    if (isReadOnlyEditor) {
        // Copying into the editor is not allowed
        className += ' cannot-copy';
    }

    return (
        <Localized id='machinery-Translation--copy' attrs={{ title: true }}>
            <li
                className={className}
                title='Copy Into Translation'
                onClick={copyTranslationIntoEditor}
            >
                <header>
                    {!translation.quality ? null : (
                        <span className='quality'>
                            {translation.quality + '%'}
                        </span>
                    )}
                    <TranslationSource
                        translation={translation}
                        locale={locale}
                    />
                </header>
                <p className='original'>
                    {translation.sources.indexOf('caighdean') === -1 ? (
                        <GenericTranslation
                            content={translation.original}
                            diffTarget={sourceString}
                        />
                    ) : (
                        /*
                         * Caighdean takes `gd` translations as input, so we shouldn't
                         * diff it against the `en-US` source string.
                         */
                        <GenericTranslation content={translation.original} />
                    )}
                </p>
                <p
                    className='suggestion'
                    dir={locale.direction}
                    data-script={locale.script}
                    lang={locale.code}
                >
                    <GenericTranslation content={translation.translation} />
                </p>
            </li>
        </Localized>
    );
}
