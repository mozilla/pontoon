import { Localized } from '@fluent/react';
import React from 'react';

import type { EditorState } from '~/core/editor';
import type { UserState } from '~/core/user';
import { useAppDispatch, useAppSelector } from '~/hooks';
import { useTranslator } from '~/hooks/useTranslator';

import { resetFailedChecks } from '../actions';
import { useUpdateTranslationStatus } from '../hooks/useUpdateTranslationStatus';

import './FailedChecks.css';

type FailedChecksProps = {
  sendTranslation: (ignoreWarnings?: boolean) => void;
};

/**
 * Shows a list of failed checks (errors and warnings) and a button to ignore
 * those checks and proceed anyway.
 */
export function FailedChecks(
  props: FailedChecksProps,
): null | React.ReactElement<'div'> {
  const dispatch = useAppDispatch();

  const errors = useAppSelector((state) => state.editor.errors);
  const warnings = useAppSelector((state) => state.editor.warnings);
  const source = useAppSelector((state) => state.editor.source);
  const userState = useAppSelector((state) => state.user);

  const updateTranslationStatus = useUpdateTranslationStatus();

  if (!errors.length && !warnings.length) {
    return null;
  }

  function resetChecks() {
    dispatch(resetFailedChecks());
  }

  function approveAnyway() {
    if (typeof source === 'number') {
      updateTranslationStatus(source, 'approve', true);
    }
  }

  function submitAnyway() {
    props.sendTranslation(true);
  }

  return (
    <div className='failed-checks'>
      <Localized id='editor-FailedChecks--close' attrs={{ ariaLabel: true }}>
        <button
          aria-label='Close failed checks popup'
          className='close'
          onClick={resetChecks}
        >
          ×
        </button>
      </Localized>
      <Localized id='editor-FailedChecks--title'>
        <p className='title'>THE FOLLOWING CHECKS HAVE FAILED</p>
      </Localized>
      <ul>
        {errors.map((error, key) => (
          <li className='error' key={key}>
            {error}
          </li>
        ))}
        {warnings.map((warning, key) => (
          <li className='warning' key={key}>
            {warning}
          </li>
        ))}
      </ul>
      <MainAction
        source={source}
        user={userState}
        errors={errors}
        approveAnyway={approveAnyway}
        submitAnyway={submitAnyway}
      />
    </div>
  );
}
type MainActionProps = {
  source: EditorState['source'];
  user: UserState;
  errors: Array<string>;
  approveAnyway: () => void;
  submitAnyway: () => void;
};

/**
 * Shows a button to ignore failed checks and proceed with the main editor action.
 */
function MainAction({
  source,
  user,
  errors,
  approveAnyway,
  submitAnyway,
}: MainActionProps) {
  const isTranslator = useTranslator();

  if (source === 'stored' || errors.length) {
    return null;
  }

  if (source !== 'submitted') {
    return (
      <Localized id='editor-FailedChecks--approve-anyway'>
        <button className='approve anyway' onClick={approveAnyway}>
          APPROVE ANYWAY
        </button>
      </Localized>
    );
  }

  if (user.settings.forceSuggestions || !isTranslator) {
    return (
      <Localized id='editor-FailedChecks--suggest-anyway'>
        <button className='suggest anyway' onClick={submitAnyway}>
          SUGGEST ANYWAY
        </button>
      </Localized>
    );
  }

  return (
    <Localized id='editor-FailedChecks--save-anyway'>
      <button className='save anyway' onClick={submitAnyway}>
        SAVE ANYWAY
      </button>
    </Localized>
  );
}
