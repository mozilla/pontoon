import * as React from 'react';
import { useSelector } from 'react-redux';

import * as editor from 'core/editor';
import * as entities from 'core/entities';
import { fluent } from 'core/utils';
import { GenericTranslationForm } from 'modules/genericeditor';

type Props = {
    ftlSwitch: React.ReactNode;
};

/**
 * Editor for simple Fluent strings.
 *
 * Handles transforming the editor's content back to a valid Fluent message on save.
 * Makes sure the content is correctly formatted when updated.
 */
export default function SimpleEditor(
    props: Props,
): null | React.ReactElement<any> {
    const updateTranslation = editor.useUpdateTranslation();
    const clearEditor = editor.useClearEditor();
    const copyOriginalIntoEditor = editor.useCopyOriginalIntoEditor();
    const sendTranslation = editor.useSendTranslation();

    const translation = useSelector((state) => state.editor.translation);
    const changeSource = useSelector((state) => state.editor.changeSource);
    const entity = useSelector((state) =>
        entities.selectors.getSelectedEntity(state),
    );

    // Transform the translation into a simple preview whenever it changes from
    // an external source.
    React.useLayoutEffect(() => {
        if (changeSource === 'internal' || typeof translation !== 'string') {
            return;
        }

        const message = fluent.parser.parseEntry(translation);
        if (
            fluent.isSimpleMessage(message) ||
            fluent.isSimpleSingleAttributeMessage(message)
        ) {
            updateTranslation(
                fluent.getSimplePreview(translation),
                changeSource,
            );
        }
    }, [translation, changeSource, updateTranslation]);

    // Reconstruct the translation into a valid Fluent message before sending it.
    function sendFluentTranslation(ignoreWarnings?: boolean) {
        if (!entity) {
            return;
        }

        if (typeof translation !== 'string') {
            // This should never happen. If it does, the developers have made a
            // mistake in the code. We need this check for TypeScript's sake though.
            throw new Error(
                'Unexpected data type for translation: ' + typeof translation,
            );
        }

        // The content was simple, reformat it to be an actual Fluent message.
        const content = fluent.serializer.serializeEntry(
            fluent.getReconstructedMessage(entity.original, translation),
        );
        sendTranslation(ignoreWarnings, content);
    }

    // If the translation is not a string, wait until the FluentEditor component fixes that.
    if (!entity || typeof translation !== 'string') {
        return null;
    }

    return (
        <>
            <GenericTranslationForm
                sendTranslation={sendFluentTranslation}
                updateTranslation={updateTranslation}
            />
            <editor.EditorMenu
                firstItemHook={props.ftlSwitch}
                translationLengthHook={
                    <editor.TranslationLength
                        comment={entity.comment}
                        format={entity.format}
                        original={fluent.getSimplePreview(entity.original)}
                        translation={fluent.getSimplePreview(translation)}
                    />
                }
                clearEditor={clearEditor}
                copyOriginalIntoEditor={copyOriginalIntoEditor}
                sendTranslation={sendFluentTranslation}
            />
        </>
    );
}
