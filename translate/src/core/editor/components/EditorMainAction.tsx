import { Localized } from '@fluent/react';
import React from 'react';

import { useAppSelector } from '~/hooks';
import { isTranslator } from '~/core/user/selectors';
import { sameExistingTranslation } from '../selectors';
import { useUpdateTranslationStatus } from '..';

type Props = {
  sendTranslation: (ignoreWarnings?: boolean) => void;
};

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
export default function EditorMainAction({
  sendTranslation,
}: Props): React.ReactElement<React.ElementType> {
  const isRunningRequest = useAppSelector(
    (state) => state.editor.isRunningRequest,
  );
  const forceSuggestions = useAppSelector(
    (state) => state.user.settings.forceSuggestions,
  );
  const isTranslator_ = useAppSelector(isTranslator);
  const sameExistingTranslation_ = useAppSelector(sameExistingTranslation);

  const updateTranslationStatus = useUpdateTranslationStatus();

  function approveTranslation() {
    if (sameExistingTranslation_) {
      updateTranslationStatus(sameExistingTranslation_.pk, 'approve');
    }
  }

  let btn: {
    id: string;
    className: string;
    action: (event: React.SyntheticEvent) => void;
    title: string;
    label: string;
    glyph: React.ReactElement<'i'> | null | undefined;
  };

  if (
    isTranslator_ &&
    sameExistingTranslation_ &&
    !sameExistingTranslation_.approved
  ) {
    // Approve button, will approve the translation.
    btn = {
      id: 'editor-EditorMenu--button-approve',
      className: 'action-approve',
      action: approveTranslation,
      title: 'Approve Translation (Enter)',
      label: 'APPROVE',
      glyph: null,
    };

    if (isRunningRequest) {
      btn.id = 'editor-EditorMenu--button-approving';
      btn.label = 'APPROVING';
      btn.glyph = <i className='fa fa-circle-notch fa-spin' />;
    }
  } else if (forceSuggestions || !isTranslator_) {
    // Suggest button, will send an unreviewed translation.
    btn = {
      id: 'editor-EditorMenu--button-suggest',
      className: 'action-suggest',
      action: () => sendTranslation(),
      title: 'Suggest Translation (Enter)',
      label: 'SUGGEST',
      glyph: null,
    };

    if (isRunningRequest) {
      btn.id = 'editor-EditorMenu--button-suggesting';
      btn.label = 'SUGGESTING';
      btn.glyph = <i className='fa fa-circle-notch fa-spin' />;
    }
  } else {
    // Save button, will send an approved translation.
    btn = {
      id: 'editor-EditorMenu--button-save',
      className: 'action-save',
      action: () => sendTranslation(),
      title: 'Save Translation (Enter)',
      label: 'SAVE',
      glyph: null,
    };

    if (isRunningRequest) {
      btn.id = 'editor-EditorMenu--button-saving';
      btn.label = 'SAVING';
      btn.glyph = <i className='fa fa-circle-notch fa-spin' />;
    }
  }

  const elems = btn.glyph ? { glyph: btn.glyph } : undefined;
  return (
    <Localized id={btn.id} attrs={{ title: true }} elems={elems}>
      <button
        className={btn.className}
        onClick={btn.action}
        title={btn.title}
        disabled={isRunningRequest}
      >
        {btn.glyph}
        {btn.label}
      </button>
    </Localized>
  );
}
