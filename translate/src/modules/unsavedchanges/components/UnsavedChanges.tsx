import React, { useEffect } from 'react';
import { Localized } from '@fluent/react';

import { useAppDispatch } from '~/hooks';

import { hideUnsavedChanges, ignoreUnsavedChanges } from '../actions';
import { useUnsavedChanges } from '../hooks';

import './UnsavedChanges.css';

/*
 * Renders the unsaved changes popup.
 */
export function UnsavedChanges(): React.ReactElement<'div'> | null {
  const dispatch = useAppDispatch();
  const { callback, ignored, shown } = useUnsavedChanges();

  useEffect(() => {
    if (ignored && callback) {
      callback();
      dispatch(hideUnsavedChanges());
    }
  }, [ignored]);

  return shown ? (
    <div className='unsaved-changes'>
      <Localized id='editor-UnsavedChanges--close' attrs={{ ariaLabel: true }}>
        <button
          aria-label='Close unsaved changes popup'
          className='close'
          onClick={() => dispatch(hideUnsavedChanges())}
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
          onClick={() => dispatch(ignoreUnsavedChanges())}
        >
          PROCEED
        </button>
      </Localized>
    </div>
  ) : null;
}
