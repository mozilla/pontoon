/* @flow */

import * as React from 'react';
import { useSelector } from 'react-redux';

import * as editor from 'core/editor';
import * as entities from 'core/entities';
import * as plural from 'core/plural';

import GenericTranslationForm from './GenericTranslationForm';

/**
 * Editor for regular translations.
 *
 * Used for all file formats except Fluent.
 *
 * Shows a plural selector, a translation form and a menu.
 */
export default function GenericEditor() {
    editor.useLoadTranslation();
    const updateTranslation = editor.useUpdateTranslation();
    const clearEditor = editor.useClearEditor();
    const copyOriginalIntoEditor = editor.useCopyOriginalIntoEditor();
    const sendTranslation = editor.useSendTranslation();

    const translation = useSelector((state) => state.editor.translation);
    const entity = useSelector((state) =>
        entities.selectors.getSelectedEntity(state),
    );
    const pluralForm = useSelector((state) =>
        plural.selectors.getPluralForm(state),
    );

    if (!entity) {
        return null;
    }

    const original = pluralForm <= 0 ? entity.original : entity.original_plural;

    return (
        <>
            <plural.PluralSelector />
            <GenericTranslationForm
                sendTranslation={sendTranslation}
                updateTranslation={updateTranslation}
            />
            <editor.EditorMenu
                translationLengthHook={
                    <editor.TranslationLength
                        comment={entity.comment}
                        format={entity.format}
                        original={original}
                        translation={translation}
                    />
                }
                clearEditor={clearEditor}
                copyOriginalIntoEditor={copyOriginalIntoEditor}
                sendTranslation={sendTranslation}
            />
        </>
    );
}
