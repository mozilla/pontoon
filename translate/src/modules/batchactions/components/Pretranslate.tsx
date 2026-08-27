import React from 'react';
import { BatchActionsState } from '../reducer';
import { Localized } from '@fluent/react';
import type { ResponseType } from '../actions';

type Props = {
  pretranslate: () => void;
  batchactions: BatchActionsState;
};
export function Pretranslate({
  pretranslate,
  batchactions: { response, requestInProgress },
}: Props): React.ReactElement<'button'> {
  return (
    <button className='pretranslate-btn' onClick={pretranslate}>
      <Title {...response} />
      {requestInProgress === 'pretranslate' ? (
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
  if (action !== 'pretranslate') {
    return (
      <Localized id='batchactions-Pretranslate--default'>
        PRETRANSLATE
      </Localized>
    );
  }

  if (error) {
    return (
      <Localized id='batchactions-Pretranslate--error'>
        OOPS, SOMETHING WENT WRONG
      </Localized>
    );
  }

  const success = (
    <Localized
      id='batchactions-Pretranslate--success'
      vars={{ changedCount: changedCount ?? -1 }}
    >
      {'{ $changedCount } STRINGS PRETRANSLATED'}
    </Localized>
  );

  return invalidCount ? (
    <>
      {success}
      {' · '}
      <Localized
        id='batchactions-Pretranslate--invalidCount'
        vars={{ invalidCount: invalidCount ?? -1 }}
      >
        {'{ $invalidCount } STRINGS WERE NOT PRETRANSLATED'}
      </Localized>
    </>
  ) : (
    success
  );
}
