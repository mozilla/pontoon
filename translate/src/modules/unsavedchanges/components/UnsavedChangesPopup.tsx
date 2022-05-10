import React, { useContext } from 'react';
import { Localized } from '@fluent/react';

import { UnsavedChanges } from '~/context/unsavedChanges';

import './UnsavedChangesPopup.css';

/*
 * Renders the unsaved changes popup.
 */
export function UnsavedChangesPopup(): React.ReactElement<'div'> | null {
  const { show, set } = useContext(UnsavedChanges);

  return show ? (
    <div className='unsaved-changes'>
      <Localized id='editor-UnsavedChanges--close' attrs={{ ariaLabel: true }}>
        <button
          aria-label='Close unsaved changes popup'
          className='close'
          onClick={() => set(null)}
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
          onClick={() => set({ ignore: true })}
        >
          PROCEED
        </button>
      </Localized>
    </div>
  ) : null;
}
