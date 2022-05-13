import { useCallback, useContext, useEffect, useState } from 'react';

import { Locale } from '~/context/Locale';
import { useTranslationForEntity } from '~/context/PluralForm';
import { EDITOR } from '~/core/editor';
import {
  setInitialTranslation,
  updateTranslation,
} from '~/core/editor/actions';
import { useSelectedEntity } from '~/core/entities/hooks';
import { convertSyntax } from '~/core/utils/fluent';
import { useAppDispatch, useAppSelector } from '~/hooks';

import { getSyntaxType } from './getSyntaxType';

/**
 * Hook to allow to force showing the source editor.
 *
 * @returns An array containing:
 *     - a boolean indicating if the source mode is enabled;
 *     - a function to toggle the source mode.
 */
export function useForceSource(): [boolean, () => void] {
  const dispatch = useAppDispatch();

  const translation = useAppSelector((state) => state[EDITOR].translation);
  const entity = useSelectedEntity();
  const activeTranslation = useTranslationForEntity(entity);
  const locale = useContext(Locale);

  // Force using the source editor.
  const [forceSource, setForceSource] = useState(false);

  // When the entity changes, reset the `forceSource` setting. Never show the source
  // editor by default.
  useEffect(() => {
    setForceSource(false);
  }, [entity]);

  // When a user wants to force (or unforce) the source editor, we need to convert
  // the existing translation to a format appropriate for the next editor type.
  const toggleForceSource = useCallback(() => {
    const syntax = getSyntaxType(translation);

    if (syntax === 'complex') {
      return;
    }
    const fromSyntax = forceSource ? 'complex' : syntax;
    const toSyntax = forceSource ? syntax : 'complex';
    const [translationContent, initialContent] = convertSyntax(
      fromSyntax,
      toSyntax,
      translation,
      entity?.original ?? '',
      activeTranslation?.string ?? '',
      locale,
    );
    dispatch(setInitialTranslation(initialContent));
    dispatch(updateTranslation(translationContent));
    setForceSource((prev) => !prev);
  }, [translation, entity, activeTranslation, locale, forceSource]);

  return [forceSource, toggleForceSource];
}
