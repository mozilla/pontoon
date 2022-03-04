import * as React from 'react';

import * as editor from '~/core/editor';
import { useSelectedEntity } from '~/core/entities/hooks';
import { PluralSelector } from '~/core/plural';
import { usePluralForm, useTranslationForEntity } from '~/context/pluralForm';
import { useAppDispatch, useAppSelector } from '~/hooks';

import GenericTranslationForm from './GenericTranslationForm';

/**
 * Hook to update the editor content whenever the entity changes.
 */
function useLoadTranslation() {
  const dispatch = useAppDispatch();

  const updateTranslation = editor.useUpdateTranslation();

  const changeSource = useAppSelector((state) => state.editor.changeSource);
  const entity = useSelectedEntity();
  const { pluralForm } = usePluralForm(entity);
  const activeTranslationString = useTranslationForEntity(entity)?.string ?? '';

  React.useLayoutEffect(() => {
    // We want to run this only when the editor state has been reset.
    if (changeSource === 'reset') {
      dispatch(editor.actions.setInitialTranslation(activeTranslationString));
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
export default function GenericEditor(): null | React.ReactElement<any> {
  const dispatch = useAppDispatch();

  useLoadTranslation();
  const updateTranslation = editor.useUpdateTranslation();
  const clearEditor = editor.useClearEditor();
  const copyOriginalIntoEditor = editor.useCopyOriginalIntoEditor();
  const sendTranslation = editor.useSendTranslation();

  const translation = useAppSelector((state) => state.editor.translation);
  const entity = useSelectedEntity();
  const { pluralForm } = usePluralForm(entity);

  if (!entity || typeof translation !== 'string') {
    return null;
  }

  function resetEditor() {
    dispatch(editor.actions.reset());
  }

  const original = pluralForm <= 0 ? entity.original : entity.original_plural;

  return (
    <>
      <PluralSelector resetEditor={resetEditor} />
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
