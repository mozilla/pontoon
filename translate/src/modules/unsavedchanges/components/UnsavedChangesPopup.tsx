import React, { useContext } from 'react';
import { Localized } from '@fluent/react';

import { UnsavedActions, UnsavedChanges } from '../../../../src/context/UnsavedChanges';

import './UnsavedChangesPopup.css';

/*
 * Renders the unsaved changes popup.
 */
export function UnsavedChangesPopup(): React.ReactElement<'div'> | null {
  const { resetUnsavedChanges } = useContext(UnsavedActions);
  const { onIgnore } = useContext(UnsavedChanges);

  return onIgnore ? (
    <div className='unsaved-changes'>
      <Localized id='editor-UnsavedChanges--close' attrs={{ ariaLabel: true }}>
        <button
          aria-label='Close unsaved changes popup'
          className='close'
          onClick={() => resetUnsavedChanges(false)}
        >
          ×
        </button>
      </Localized>

      <Localized id='editor-UnsavedChanges--title'>
        <p className='title'>YOU HAVE UNSAVED CHANGES</p>
      </Localized>

      <Localized id='editor-UnsavedChanges--body'>
        <p className='body'>Are you sure you want to proceed?</p>
      </Localized>

      <Localized id='editor-UnsavedChanges--proceed'>
        <button
          className='proceed anyway'
          onClick={() => resetUnsavedChanges(true)}
        >
          PROCEED
        </button>
      </Localized>
    </div>
  ) : null;
}
