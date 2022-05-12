import React from 'react';

import {
  EditorMenu,
  TranslationLength,
  useClearEditor,
  useCopyOriginalIntoEditor,
  useSendTranslation,
  useUpdateTranslation,
} from '~/core/editor';
import { resetEditor, setInitialTranslation } from '~/core/editor/actions';
import { useSelectedEntity } from '~/core/entities/hooks';
import { usePluralForm, useTranslationForEntity } from '~/context/pluralForm';
import { useAppDispatch, useAppSelector } from '~/hooks';

import { GenericTranslationForm } from './GenericTranslationForm';
import { PluralSelector } from './PluralSelector';

/**
 * Hook to update the editor content whenever the entity changes.
 */
function useLoadTranslation() {
  const dispatch = useAppDispatch();

  const updateTranslation = useUpdateTranslation();

  const changeSource = useAppSelector((state) => state.editor.changeSource);
  const entity = useSelectedEntity();
  const { pluralForm } = usePluralForm(entity);
  const activeTranslationString = useTranslationForEntity(entity)?.string ?? '';

  React.useLayoutEffect(() => {
    // We want to run this only when the editor state has been reset.
    if (changeSource === 'reset') {
      dispatch(setInitialTranslation(activeTranslationString));
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
export function GenericEditor(): null | React.ReactElement<any> {
  const dispatch = useAppDispatch();

  useLoadTranslation();
  const updateTranslation = useUpdateTranslation();
  const clearEditor = useClearEditor();
  const copyOriginalIntoEditor = useCopyOriginalIntoEditor();
  const sendTranslation = useSendTranslation();

  const translation = useAppSelector((state) => state.editor.translation);
  const entity = useSelectedEntity();
  const { pluralForm } = usePluralForm(entity);

  if (!entity || typeof translation !== 'string') {
    return null;
  }

  const original = pluralForm <= 0 ? entity.original : entity.original_plural;

  return (
    <>
      <PluralSelector resetEditor={() => dispatch(resetEditor())} />
      <GenericTranslationForm
        sendTranslation={sendTranslation}
        updateTranslation={updateTranslation}
      />
      <EditorMenu
        translationLengthHook={
          <TranslationLength
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
