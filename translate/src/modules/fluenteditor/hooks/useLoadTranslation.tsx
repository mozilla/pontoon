import { Entry } from '@fluent/syntax';
import { useContext, useLayoutEffect } from 'react';

import { Locale } from '~/context/locale';
import { useTranslationForEntity } from '~/context/pluralForm';
import { EDITOR } from '~/core/editor';
import {
  setInitialTranslation,
  updateTranslation,
} from '~/core/editor/actions';
import { useSelectedEntity } from '~/core/entities/hooks';
import {
  flattenMessage,
  getEmptyMessage,
  getSimplePreview,
  parser,
} from '~/core/utils/fluent';
import { useAppDispatch, useAppSelector } from '~/hooks';

import { getSyntaxType } from './getSyntaxType';

/**
 * Hook to update the editor content whenever the entity changes.
 *
 * This hook is in charge of formatting the translation content for each type of Fluent Editor.
 * It does *not* update that content when the user switches the "force source" mode though,
 * as that is dealt with by using the `useForceSource` hook.
 */
export function useLoadTranslation() {
  const dispatch = useAppDispatch();

  const locale = useContext(Locale);
  const entity = useSelectedEntity();
  const activeTranslationString = useTranslationForEntity(entity)?.string ?? '';
  const changeSource = useAppSelector((state) => state[EDITOR].changeSource);

  useLayoutEffect(() => {
    if (!entity || changeSource !== 'reset') {
      return;
    }

    let translationContent: string | Entry;
    const syntax = getSyntaxType(activeTranslationString || entity.original);
    switch (syntax) {
      case 'complex':
        // Use the actual content that we get from the server: a Fluent message as a string.
        translationContent = activeTranslationString;
        break;

      case 'simple':
        // Use a simplified preview of the Fluent message.
        translationContent = getSimplePreview(activeTranslationString);
        break;

      case 'rich':
        // Use a Fluent Message object.
        translationContent = activeTranslationString
          ? flattenMessage(parser.parseEntry(activeTranslationString))
          : getEmptyMessage(parser.parseEntry(entity.original), locale);
        break;
    }

    dispatch(setInitialTranslation(translationContent));
    dispatch(updateTranslation(translationContent, 'initial'));
  }, [changeSource, entity, activeTranslationString, locale]);
}
