import { Localized } from '@fluent/react';
import React, { useContext } from 'react';
import { EditorData } from '~/context/Editor';

import { useAppSelector } from '~/hooks';
import { useTranslator } from '~/hooks/useTranslator';

import { useExistingTranslationGetter } from '../hooks/useExistingTranslationGetter';
import { useSendTranslation } from '../hooks/useSendTranslation';
import { useUpdateTranslationStatus } from '../hooks/useUpdateTranslationStatus';

/**
 * Render the main action button of the Editor.
 *
 * This component renders a button to "Save", "Suggest" or "Approve" a translation.
 *
 * It renders "Approve" if the translation in the Editor is the same as an
 * already existing translation for that same entity and locale, and the user
 * has permission to approve.
 * Otherwise, if the "force suggestion" user setting is on, it renders "Suggest".
 * Otherwise, it renders "Save".
 */
export function EditorMainAction(): React.ReactElement<React.ElementType> {
  const forceSuggestions = useAppSelector(
    (state) => state.user.settings.forceSuggestions,
  );
  const isTranslator = useTranslator();
  const existingTranslation = useExistingTranslationGetter()();
  const sendTranslation = useSendTranslation();
  const updateTranslationStatus = useUpdateTranslationStatus();
  const { busy } = useContext(EditorData);

  let action:
    | 'approve'
    | 'approving'
    | 'suggest'
    | 'suggesting'
    | 'save'
    | 'saving';
  let onClick: (event: React.SyntheticEvent) => void;
  let title: string;

  if (isTranslator && existingTranslation && !existingTranslation.approved) {
    // Button to approve the translation
    action = 'approve';
    onClick = () =>
      updateTranslationStatus(existingTranslation.pk, 'approve', false);
    title = 'Approve Translation (Enter)';
  } else if (forceSuggestions || !isTranslator) {
    // Button to send an unreviewed translation
    action = 'suggest';
    onClick = () => sendTranslation();
    title = 'Suggest Translation (Enter)';
  } else {
    // Button to send an approved translation
    action = 'save';
    onClick = () => sendTranslation();
    title = 'Save Translation (Enter)';
  }

  const className = `action-${action}`;

  if (busy) {
    if (action === 'approve') {
      action = 'approving';
    } else if (action === 'save') {
      action = 'saving';
    } else {
      action = 'suggesting';
    }
  }
  const id = `editor-EditorMenu--button-${action}`;
  const label = action.toUpperCase();

  if (busy) {
    const glyph = <i className='fa fa-circle-notch fa-spin' />;
    return (
      <Localized id={id} attrs={{ title: true }} elems={{ glyph }}>
        <button className={className} disabled title={title}>
          {glyph}
          {label}
        </button>
      </Localized>
    );
  } else {
    return (
      <Localized id={id} attrs={{ title: true }}>
        <button className={className} onClick={onClick} title={title}>
          {label}
        </button>
      </Localized>
    );
  }
}
