/* @flow */

import * as React from 'react';
import { useDispatch, useSelector } from 'react-redux';

import * as editor from 'core/editor';
import * as entities from 'core/entities';
import * as plural from 'core/plural';

import GenericTranslationForm from './GenericTranslationForm';

/**
 * Hook to update the editor content whenever the entity changes.
 */
function useLoadTranslation() {
    const dispatch = useDispatch();

    const updateTranslation = editor.useUpdateTranslation();

    const changeSource = useSelector((state) => state.editor.changeSource);
    const entity = useSelector((state) =>
        entities.selectors.getSelectedEntity(state),
    );
    const pluralForm = useSelector((state) =>
        plural.selectors.getPluralForm(state),
    );
    const activeTranslationString = useSelector((state) =>
        plural.selectors.getTranslationStringForSelectedEntity(state),
    );

    React.useLayoutEffect(() => {
        // We want to run this only when the editor state has been reset.
        if (changeSource === 'reset') {
            dispatch(
                editor.actions.setInitialTranslation(activeTranslationString),
            );
            updateTranslation(activeTranslationString, 'initial');
        }
    }, [
        entity,
        changeSource,
        pluralForm,
        activeTranslationString,
        updateTranslation,
        dispatch,
    ]);
}

/**
 * Editor for regular translations.
 *
 * Used for all file formats except Fluent.
 *
 * Shows a plural selector, a translation form and a menu.
 */
export default function GenericEditor(): null | React.Element<any> {
    const dispatch = useDispatch();

    useLoadTranslation();
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

    function resetEditor() {
        dispatch(editor.actions.reset());
    }

    const original = pluralForm <= 0 ? entity.original : entity.original_plural;

    return (
        <>
            <plural.PluralSelector resetEditor={resetEditor} />
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
