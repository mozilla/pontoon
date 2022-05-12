import type { Entry } from '@fluent/syntax';
import React, { useContext, useLayoutEffect } from 'react';

import { Locale } from '~/context/locale';
import { useTranslationForEntity } from '~/context/pluralForm';
import { Translation, useUpdateTranslation } from '~/core/editor';
import {
  setInitialTranslation,
  updateTranslation,
} from '~/core/editor/actions';
import { useSelectedEntity } from '~/core/entities/hooks';
import { addNotification } from '~/core/notification/actions';
import { notificationMessages } from '~/core/notification/messages';
import * as fluent from '~/core/utils/fluent';
import type { SyntaxType } from '~/core/utils/fluent/types';
import { useAppDispatch, useAppSelector } from '~/hooks';
import { useReadonlyEditor } from '~/hooks/useReadonlyEditor';

import './FluentEditor.css';
import { RichEditor } from './rich/RichEditor';
import { SimpleEditor } from './simple/SimpleEditor';
import { SourceEditor } from './source/SourceEditor';

/**
 * Function to analyze a translation and determine what its appropriate syntax is.
 *
 * @returns The syntax of the translation, can be "simple", "rich" or "complex".
 *      - "simple" if the translation can be shown as a simple preview
 *      - "rich" if the translation is not simple but can be handled by the Rich editor
 *      - "complex" otherwise
 */
function getSyntaxType(source: string | Translation): SyntaxType {
  if (source && typeof source !== 'string') {
    return fluent.getSyntaxType(source);
  }

  const message = fluent.parser.parseEntry(source);

  // In case a simple message gets analyzed again.
  if (message.type === 'Junk') {
    return 'simple';
  }

  // Figure out and set the syntax type.
  return fluent.getSyntaxType(message);
}

/**
 * Hook to update the editor content whenever the entity changes.
 *
 * This hook is in charge of formatting the translation content for each type of Fluent Editor.
 * It does *not* update that content when the user switches the "force source" mode though,
 * as that is dealt with by using the `useForceSource` hook.
 */
function useLoadTranslation(forceSource: boolean) {
  const dispatch = useAppDispatch();

  const updateTranslation = useUpdateTranslation();
  const changeSource = useAppSelector((state) => state.editor.changeSource);

  const entity = useSelectedEntity();
  const locale = useContext(Locale);
  const activeTranslationString = useTranslationForEntity(entity)?.string ?? '';

  // We do not want to perform any formatting when the user switches "force source",
  // as that is handled in the `useForceSource` hook. We thus keep track of that variable's
  // value and only update when it didn't change since the last render.
  const prevForceSource = React.useRef(forceSource);

  useLayoutEffect(() => {
    if (
      prevForceSource.current !== forceSource ||
      !entity ||
      // We want to run this only when the editor state has been reset.
      changeSource !== 'reset'
    ) {
      prevForceSource.current = forceSource;
      return;
    }

    const syntax = getSyntaxType(activeTranslationString || entity.original);

    let translationContent: string | Entry = '';
    if (syntax === 'complex') {
      // Use the actual content that we get from the server: a Fluent message as a string.
      translationContent = activeTranslationString;
    } else if (syntax === 'simple') {
      // Use a simplified preview of the Fluent message.
      translationContent = fluent.getSimplePreview(activeTranslationString);
    } else if (syntax === 'rich') {
      // Use a Fluent Message object.
      if (activeTranslationString) {
        translationContent = fluent.flattenMessage(
          fluent.parser.parseEntry(activeTranslationString),
        );
      } else {
        translationContent = fluent.getEmptyMessage(
          fluent.parser.parseEntry(entity.original),
          locale,
        );
      }
    }
    dispatch(setInitialTranslation(translationContent));
    updateTranslation(translationContent, 'initial');
  }, [
    changeSource,
    forceSource,
    entity,
    activeTranslationString,
    locale,
    updateTranslation,
    dispatch,
  ]);
}

/**
 * Hook to allow to force showing the source editor.
 *
 * @returns { Array<boolean, Function> } An array containing:
 *      - a boolean indicating if the source mode is enabled;
 *      - a function to toggle the source mode.
 */
function useForceSource(): [boolean, () => void] {
  const dispatch = useAppDispatch();

  const translation = useAppSelector((state) => state.editor.translation);
  const entity = useSelectedEntity();
  const activeTranslation = useTranslationForEntity(entity);
  const locale = useContext(Locale);

  // Force using the source editor.
  const [forceSource, setForceSource] = React.useState(false);

  // When the entity changes, reset the `forceSource` setting. Never show the source
  // editor by default.
  React.useEffect(() => {
    setForceSource(false);
  }, [entity]);

  // When a user wants to force (or unforce) the source editor, we need to convert
  // the existing translation to a format appropriate for the next editor type.
  function changeForceSource() {
    const syntax = getSyntaxType(translation);

    if (syntax === 'complex') {
      return;
    }
    const fromSyntax = forceSource ? 'complex' : syntax;
    const toSyntax = forceSource ? syntax : 'complex';
    const [translationContent, initialContent] = fluent.convertSyntax(
      fromSyntax,
      toSyntax,
      translation,
      entity?.original ?? '',
      activeTranslation?.string ?? '',
      locale,
    );
    dispatch(setInitialTranslation(initialContent));
    dispatch(updateTranslation(translationContent));
    setForceSource(!forceSource);
  }

  return [forceSource, changeForceSource];
}

/**
 * Editor dedicated to modifying Fluent strings.
 *
 * Renders the most appropriate type of editor for the current translation.
 */
export function FluentEditor(): null | React.ReactElement<React.ElementType> {
  const dispatch = useAppDispatch();

  const translation = useAppSelector((state) => state.editor.translation);
  const readonly = useReadonlyEditor();
  const entity = useSelectedEntity();
  const activeTranslation = useTranslationForEntity(entity);
  const user = useAppSelector((state) => state.user);

  const [forceSource, changeForceSource] = useForceSource();
  useLoadTranslation(forceSource);

  if (!entity) {
    return null;
  }

  const syntax = getSyntaxType(
    translation || activeTranslation?.string || entity.original,
  );

  // Choose which editor implementation to render.
  const Editor =
    forceSource || syntax === 'complex'
      ? SourceEditor
      : syntax === 'simple'
      ? SimpleEditor
      : RichEditor;

  // When the syntax is complex, the editor is blocked in source mode, and it
  // becomes impossible to switch to a different editor type. Thus we show a
  // notification to the user if they try to use the "FTL" switch button.
  function showUnsupportedMessage() {
    dispatch(
      addNotification(notificationMessages.FTL_NOT_SUPPORTED_RICH_EDITOR),
    );
  }

  // Show a button to allow switching to the source editor.
  let ftlSwitch = null;
  // But only if the user is logged in and the string is not read-only.
  if (user.isAuthenticated && !readonly) {
    if (syntax === 'complex') {
      // TODO: To Localize
      ftlSwitch = (
        <button
          className='ftl active'
          title='Advanced FTL mode enabled'
          onClick={showUnsupportedMessage}
        >
          FTL
        </button>
      );
    } else {
      // TODO: To Localize
      ftlSwitch = (
        <button
          className={'ftl' + (forceSource ? ' active' : '')}
          title='Toggle between simple and advanced FTL mode'
          onClick={changeForceSource}
        >
          FTL
        </button>
      );
    }
  }

  return <Editor ftlSwitch={ftlSwitch} />;
}
