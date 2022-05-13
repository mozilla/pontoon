import React, { useContext, useLayoutEffect } from 'react';

import { Locale } from '~/context/Locale';
import {
  EditorMenu,
  useSendTranslation,
  useUpdateTranslation,
} from '~/core/editor';
import { useSelectedEntity } from '~/core/entities/hooks';
import * as fluent from '~/core/utils/fluent';
import { useAppDispatch, useAppSelector } from '~/hooks';

import { RichTranslationForm } from './RichTranslationForm';

type Props = {
  ftlSwitch: React.ReactNode;
};

/**
 * Rich Editor for supported Fluent strings.
 *
 * This shows the Fluent translation based on its AST, presenting a nicer
 * interface to the user. The translation is stored as an AST, and changes
 * are made directly to that AST. That is why lots of Editor methods are
 * overwritten, to handle the conversion from AST to string and back.
 */
export function RichEditor(props: Props): React.ReactElement<any> {
  const dispatch = useAppDispatch();

  const sendTranslation = useSendTranslation();
  const updateTranslation = useUpdateTranslation();

  const translation = useAppSelector((state) => state.editor.translation);
  const entity = useSelectedEntity();
  const changeSource = useAppSelector((state) => state.editor.changeSource);
  const locale = useContext(Locale);

  /**
   * Hook that makes sure the translation is a Fluent message.
   */
  useLayoutEffect(() => {
    if (typeof translation === 'string') {
      const message = fluent.parser.parseEntry(translation);
      // We need to check the syntax, because it can happen that a
      // translation changes syntax, for example if loading a new one
      // from history. In such cases, this RichEditor will render with
      // the new translation, but must not re-format it. We thus make sure
      // that the syntax of the translation is "rich" before we update it.
      const syntax = fluent.getSyntaxType(message);
      if (syntax !== 'rich') {
        return;
      }
      updateTranslation(fluent.flattenMessage(message), changeSource);
    }
  }, [translation, changeSource, updateTranslation, dispatch]);

  function clearEditor() {
    if (entity) {
      updateTranslation(
        fluent.getEmptyMessage(
          fluent.parser.parseEntry(entity.original),
          locale,
        ),
      );
    }
  }

  function copyOriginalIntoEditor() {
    if (entity) {
      const origMsg = fluent.parser.parseEntry(entity.original);
      updateTranslation(fluent.flattenMessage(origMsg));
    }
  }

  function sendFluentTranslation(ignoreWarnings?: boolean) {
    const fluentString = fluent.serializer.serializeEntry(translation);
    sendTranslation(ignoreWarnings, fluentString);
  }

  return (
    <>
      <RichTranslationForm
        clearEditor={clearEditor}
        copyOriginalIntoEditor={copyOriginalIntoEditor}
        sendTranslation={sendFluentTranslation}
        updateTranslation={updateTranslation}
      />
      <EditorMenu
        firstItemHook={props.ftlSwitch}
        clearEditor={clearEditor}
        copyOriginalIntoEditor={copyOriginalIntoEditor}
        sendTranslation={sendFluentTranslation}
      />
    </>
  );
}
