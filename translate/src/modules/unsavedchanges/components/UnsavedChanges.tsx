import React, { useEffect } from 'react';
import { connect } from 'react-redux';
import { Localized } from '@fluent/react';

import './UnsavedChanges.css';

import { NAME } from '..';

import type { UnsavedChangesState } from '../reducer';
import { AppDispatch, RootState } from '~/store';
import {
  hide as hideUnsavedChanges,
  ignore as ignoreUnsavedChanges,
} from '../actions';

type Props = {
  unsavedchanges: UnsavedChangesState;
};

type InternalProps = Props & {
  dispatch: AppDispatch;
};

/*
 * Renders the unsaved changes popup.
 */
export function UnsavedChangesBase({
  dispatch,
  unsavedchanges: { callback, ignored, shown },
}: InternalProps): React.ReactElement<'div'> | null {
  useEffect(() => {
    if (ignored && callback) {
      callback();
      dispatch(hideUnsavedChanges());
    }
  }, [ignored]);

  if (!shown) {
    return null;
  }

  return (
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
  );
}

const mapStateToProps = (state: RootState): Props => {
  return {
    unsavedchanges: state[NAME],
  };
};

export default connect(mapStateToProps)(UnsavedChangesBase) as any;
