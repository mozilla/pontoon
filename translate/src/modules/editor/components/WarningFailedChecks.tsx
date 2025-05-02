import { Localized } from '@fluent/react';
import React, { useContext } from 'react';
import { FailedChecksData } from '~/context/FailedChecksData';
import './FailedChecks.css';

/**
 * Displays a list of failed checks (errors and warnings) without any actions.
 */
export function WarningFailedChecks(): null | React.ReactElement<'div'> {
  const { errors, warnings } = useContext(FailedChecksData);

  if (!errors.length && !warnings.length) {
    return null;
  }

  return (
    <div className='failed-checks'>
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
    </div>
  );
}
