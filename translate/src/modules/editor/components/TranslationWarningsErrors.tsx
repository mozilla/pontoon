import { Localized } from '@fluent/react';
import React, { useContext } from 'react';

import './TranslationWarningsErrors.css';

import { FailedChecksData } from '~/context/FailedChecksData';

export function TranslationWarningsErrors(): React.ReactElement<'div'> | null {
  const { errors, warnings } = useContext(FailedChecksData);

  // If there are no warnings or errors, don't render anything
  if (errors.length === 0 && warnings.length === 0) {
    return null;
  }

  return (
    <div className='translation-warnings'>
      {errors.length > 0 && (
        <div className='translation-errors'>
          <Localized id='editor-TranslationWarnings--errors-title'>
            <h3>Errors</h3>
          </Localized>
          <ul>
            {errors.map((error, index) => (
              <li key={index} className='error-item'>
                <i className='fa fa-times-circle'></i> {error}
              </li>
            ))}
          </ul>
        </div>
      )}

      {warnings.length > 0 && (
        <div className='translation-warnings-list'>
          <Localized id='editor-FailedChecks--title'>
            <h3>Warnings</h3>
          </Localized>
          <ul>
            {warnings.map((warning, index) => (
              <li key={index} className='warning-item'>
                <i className='fa fa-exclamation-triangle'></i> {warning}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
