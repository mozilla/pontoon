import { Localized } from '@fluent/react';
import React, { useContext } from 'react';
import { FailedChecksData } from '~/context/FailedChecksData';

import { useAppSelector } from '~/hooks';
import { useTranslator } from '~/hooks/useTranslator';
import { useSendTranslation } from '../hooks/useSendTranslation';

import { useUpdateTranslationStatus } from '../hooks/useUpdateTranslationStatus';

import './FailedChecks.css';

/**
 * Shows a list of failed checks (errors and warnings) and a button to ignore
 * those checks and proceed anyway.
 */
export function FailedChecks(): null | React.ReactElement<'div'> {
  const sendTranslation = useSendTranslation();
  const updateTranslationStatus = useUpdateTranslationStatus();
  const { errors, warnings, source, resetFailedChecks } =
    useContext(FailedChecksData);
  const { settings } = useAppSelector((state) => state.user);
  const isTranslator = useTranslator();

  if (!errors.length && !warnings.length) {
    return null;
  }

  function approveAnyway() {
    if (typeof source === 'number') {
      updateTranslationStatus(source, 'approve', true);
    }
  }

  function submitAnyway() {
    sendTranslation(true);
  }

  return (
    <div className='failed-checks'>
      <Localized id='editor-FailedChecks--close' attrs={{ ariaLabel: true }}>
        <button
          aria-label='Close failed checks popup'
          className='close'
          onClick={resetFailedChecks}
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
        source={errors.length ? null : source}
        suggesting={settings.forceSuggestions || !isTranslator}
        approveAnyway={approveAnyway}
        submitAnyway={submitAnyway}
      />
    </div>
  );
}
type MainActionProps = {
  source: FailedChecksData['source'];
  suggesting: boolean;
  approveAnyway: () => void;
  submitAnyway: () => void;
};

/**
 * Shows a button to ignore failed checks and proceed with the main editor action.
 */
function MainAction({
  source,
  suggesting,
  approveAnyway,
  submitAnyway,
}: MainActionProps) {
  if (source === 'submitted') {
    return suggesting ? (
      <Localized id='editor-FailedChecks--suggest-anyway'>
        <button className='suggest anyway' onClick={submitAnyway}>
          SUGGEST ANYWAY
        </button>
      </Localized>
    ) : (
      <Localized id='editor-FailedChecks--save-anyway'>
        <button className='save anyway' onClick={submitAnyway}>
          SAVE ANYWAY
        </button>
      </Localized>
    );
  } else if (typeof source === 'number') {
    return (
      <Localized id='editor-FailedChecks--approve-anyway'>
        <button className='approve anyway' onClick={approveAnyway}>
          APPROVE ANYWAY
        </button>
      </Localized>
    );
  } else {
    return null;
  }
}
