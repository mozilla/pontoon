import React, { useCallback, useLayoutEffect } from 'react';

import {
  EDITOR,
  EditorMenu,
  TranslationLength,
  useClearEditor,
  useCopyOriginalIntoEditor,
  useSendTranslation,
  useUpdateTranslation,
} from '~/core/editor';
import { useSelectedEntity } from '~/core/entities/hooks';
import {
  getReconstructedMessage,
  getSimplePreview,
  isSimpleMessage,
  isSimpleSingleAttributeMessage,
  parseEntry,
  serializeEntry,
} from '~/core/utils/fluent';
import { useAppSelector } from '~/hooks';
import { GenericTranslationForm } from '~/modules/genericeditor';

type Props = {
  ftlSwitch: React.ReactNode;
};

/**
 * Editor for simple Fluent strings.
 *
 * Handles transforming the editor's content back to a valid Fluent message on save.
 * Makes sure the content is correctly formatted when updated.
 */
export function SimpleEditor({ ftlSwitch }: Props): React.ReactElement | null {
  const updateTranslation = useUpdateTranslation();
  const clearEditor = useClearEditor();
  const copyOriginalIntoEditor = useCopyOriginalIntoEditor();
  const sendTranslation = useSendTranslation();

  const translation = useAppSelector((state) => state[EDITOR].translation);
  const changeSource = useAppSelector((state) => state[EDITOR].changeSource);
  const entity = useSelectedEntity();

  // Transform the translation into a simple preview whenever it changes from
  // an external source.
  useLayoutEffect(() => {
    if (changeSource === 'internal' || typeof translation !== 'string') {
      return;
    }

    const message = parseEntry(translation);
    if (isSimpleMessage(message) || isSimpleSingleAttributeMessage(message)) {
      updateTranslation(getSimplePreview(translation), changeSource);
    }
  }, [translation, changeSource, updateTranslation]);

  // Reconstruct the translation into a valid Fluent message before sending it.
  const sendFluentTranslation = useCallback(
    (ignoreWarnings?: boolean) => {
      if (entity) {
        if (typeof translation !== 'string') {
          // This should never happen. If it does, the developers have made a
          // mistake in the code. We need this check for TypeScript's sake though.
          throw new Error(
            'Unexpected data type for translation: ' + typeof translation,
          );
        }

        // The content was simple, reformat it to be an actual Fluent message.
        const content = serializeEntry(
          getReconstructedMessage(entity.original, translation),
        );
        sendTranslation(ignoreWarnings, content);
      }
    },
    [entity, translation],
  );

  // If the translation is not a string, wait until the FluentEditor component fixes that.
  return entity && typeof translation === 'string' ? (
    <>
      <GenericTranslationForm
        sendTranslation={sendFluentTranslation}
        updateTranslation={updateTranslation}
      />
      <EditorMenu
        firstItemHook={ftlSwitch}
        translationLengthHook={
          <TranslationLength
            comment={entity.comment}
            format={entity.format}
            original={getSimplePreview(entity.original)}
            translation={getSimplePreview(translation)}
          />
        }
        clearEditor={clearEditor}
        copyOriginalIntoEditor={copyOriginalIntoEditor}
        sendTranslation={sendFluentTranslation}
      />
    </>
  ) : null;
}
