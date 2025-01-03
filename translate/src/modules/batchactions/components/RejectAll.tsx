import { Localized } from '@fluent/react';
import React, { useCallback, useState } from 'react';

import type { ResponseType } from '../actions';
import type { BatchActionsState } from '../reducer';

type Props = {
  rejectAll: () => void;
  batchactions: BatchActionsState;
};

/**
 * Renders Reject All batch action button.
 */
export function RejectAll({
  batchactions: { response, requestInProgress },
  rejectAll,
}: Props): React.ReactElement<'button'> {
  const [confirmationVisible, setConfirmationVisible] = useState(false);

  const handleRejectAll = useCallback(() => {
    if (confirmationVisible) {
      rejectAll();
    }
    setConfirmationVisible(!confirmationVisible);
  }, [confirmationVisible, rejectAll]);

  return (
    <button className='reject-all' onClick={handleRejectAll}>
      <Title
        confirmationVisible={confirmationVisible}
        response={response ?? {}}
      />
      {requestInProgress === 'reject' ? (
        <i className='fas fa-2x fa-circle-notch fa-spin'></i>
      ) : null}
    </button>
  );
}

function Title({
  confirmationVisible,
  response,
}: {
  confirmationVisible: boolean;
  response: Partial<ResponseType>;
}) {
  const { action, changedCount, error, invalidCount } = response;

  if (action !== 'reject') {
    return confirmationVisible ? (
      <Localized id='batchactions-RejectAll--confirmation'>
        ARE YOU SURE?
      </Localized>
    ) : (
      <Localized id='batchactions-RejectAll--default'>
        REJECT ALL SUGGESTIONS
      </Localized>
    );
  }

  if (error) {
    return (
      <Localized id='batchactions-RejectAll--error'>
        OOPS, SOMETHING WENT WRONG
      </Localized>
    );
  }

  const success = (
    <Localized
      id='batchactions-RejectAll--success'
      vars={{ changedCount: changedCount ?? -1 }}
    >
      {'{ $changedCount } STRINGS REJECTED'}
    </Localized>
  );

  return invalidCount ? (
    <>
      {success}
      {' · '}
      <Localized id='batchactions-RejectAll--invalid' vars={{ invalidCount }}>
        {'{ $invalidCount } FAILED'}
      </Localized>
    </>
  ) : (
    success
  );
}
