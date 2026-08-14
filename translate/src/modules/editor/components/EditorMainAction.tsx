import { useLocalization } from '@fluent/react';
import classNames from 'classnames';
import React, { useContext } from 'react';

import { EditorData, EditorResult } from '~/context/Editor';
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
  const { l10n } = useLocalization();
  const isTranslator = useTranslator();
  const existingTranslation = useExistingTranslationGetter()();
  const sendTranslation = useSendTranslation();
  const updateTranslationStatus = useUpdateTranslationStatus();
  const { busy } = useContext(EditorData);
  const entry = useContext(EditorResult);

  let action:
    | 'approve'
    | 'approving'
    | 'suggest'
    | 'suggesting'
    | 'save'
    | 'saving';
  let onClick: (event: React.SyntheticEvent) => void;
  let error = entry ? null : 'syntax-error';

  if (
    isTranslator &&
    existingTranslation &&
    existingTranslation.status !== 'approved'
  ) {
    action = 'approve';
    onClick = () =>
      updateTranslationStatus(existingTranslation.pk, 'approve', false);
  } else {
    action = forceSuggestions || !isTranslator ? 'suggest' : 'save';
    onClick = () => sendTranslation();
    error ??= existingTranslation ? 'same-translation' : null;
  }

  const className = classNames(`action-${action}`, error && 'has-error');

  if (busy && !error) {
    if (action === 'approve') {
      action = 'approving';
    } else if (action === 'save') {
      action = 'saving';
    } else {
      action = 'suggesting';
    }
  }
  const label = l10n.getString(
    `editor-EditorMenu--button-${action}`,
    null,
    action.toUpperCase(),
  );
  const title = l10n.getString(
    `editor-EditorMenu--title-${error ?? action}`,
    null,
    ' ',
  );

  if (busy && !error) {
    const glyph = <i className='fas fa-circle-notch fa-spin' />;
    return (
      <button className={className} disabled title={title}>
        {glyph}
        {label}
      </button>
    );
  } else {
    return (
      <button className={className} onClick={onClick} title={title}>
        {label}
      </button>
    );
  }
}
