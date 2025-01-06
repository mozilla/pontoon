import { Localized } from '@fluent/react';
import React from 'react';

import type { ResponseType } from '../actions';
import type { BatchActionsState } from '../reducer';

type Props = {
  replaceAll: () => void;
  batchactions: BatchActionsState;
};

/**
 * Renders Replace All batch action button.
 */
export function ReplaceAll({
  replaceAll,
  batchactions: { response, requestInProgress },
}: Props): React.ReactElement<'button'> {
  return (
    <button className='replace-all' onClick={replaceAll}>
      <Title {...response} />
      {requestInProgress !== 'replace' ? null : (
        <i className='fas fa-2x fa-circle-notch fa-spin'></i>
      )}
    </button>
  );
}

function Title({
  action,
  changedCount,
  error,
  invalidCount,
}: Partial<ResponseType>) {
  if (action !== 'replace') {
    return (
      <Localized id='batchactions-ReplaceAll--default'>REPLACE ALL</Localized>
    );
  }

  if (error) {
    return (
      <Localized id='batchactions-ReplaceAll--error'>
        OOPS, SOMETHING WENT WRONG
      </Localized>
    );
  }

  const success = (
    <Localized
      id='batchactions-ReplaceAll--success'
      vars={{ changedCount: changedCount ?? -1 }}
    >
      {'{ $changedCount } STRINGS REPLACED'}
    </Localized>
  );

  return invalidCount ? (
    <>
      {success}
      {' · '}
      <Localized id='batchactions-ReplaceAll--invalid' vars={{ invalidCount }}>
        {'{ $invalidCount } FAILED'}
      </Localized>
    </>
  ) : (
    success
  );
}
