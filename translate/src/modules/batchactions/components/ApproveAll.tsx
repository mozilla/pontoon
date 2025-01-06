import { Localized } from '@fluent/react';
import React from 'react';

import type { ResponseType } from '../actions';
import type { BatchActionsState } from '../reducer';

type Props = {
  approveAll: () => void;
  batchactions: BatchActionsState;
};

/**
 * Renders Approve All batch action button.
 */
export function ApproveAll({
  approveAll,
  batchactions: { response, requestInProgress },
}: Props): React.ReactElement<'button'> {
  return (
    <button className='approve-all' onClick={approveAll}>
      <Title {...response} />
      {requestInProgress === 'approve' ? (
        <i className='fas fa-2x fa-circle-notch fa-spin'></i>
      ) : null}
    </button>
  );
}

function Title({
  action,
  changedCount,
  error,
  invalidCount,
}: Partial<ResponseType>) {
  if (action !== 'approve') {
    return (
      <Localized id='batchactions-ApproveAll--default'>APPROVE ALL</Localized>
    );
  }

  if (error) {
    return (
      <Localized id='batchactions-ApproveAll--error'>
        OOPS, SOMETHING WENT WRONG
      </Localized>
    );
  }

  const success = (
    <Localized
      id='batchactions-ApproveAll--success'
      vars={{ changedCount: changedCount ?? -1 }}
    >
      {'{ $changedCount } STRINGS APPROVED'}
    </Localized>
  );

  return invalidCount ? (
    <>
      {success}
      {' · '}
      <Localized id='batchactions-ApproveAll--invalid' vars={{ invalidCount }}>
        {'{ $invalidCount } FAILED'}
      </Localized>
    </>
  ) : (
    success
  );
}
