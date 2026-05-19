import React from 'react';
import type { BatchActionsState } from '../reducer';
import { Localized } from '@fluent/react';
import type { ResponseType } from '../actions';

type Props = {
  copyFromLocale: () => void;
  batchactions: BatchActionsState;
};

/**
 * Renders Copy From a Similar Locale batch action button
 */
export function CopyFromLocale({
  copyFromLocale,
  batchactions: { response, requestInProgress },
}: Props): React.ReactElement<'button'> {
  return (
    <button className='copy-from-locale-btn' onClick={copyFromLocale}>
      <Title {...response} />
    </button>
  );
}

function Title({
  action,
  changedCount,
  error,
  invalidCount,
}: Partial<ResponseType>) {
  if (action !== 'copy_from_locale') {
    return (
      <Localized id='batchactions-CopyFromLocale--default'>
        COPY AS SUGGESTIONS
      </Localized>
    );
  }

  if (error) {
    return (
      <Localized id='batchactions-CopyFromLocale--error'>
        OOPS, SOMETHING WENT WRONG
      </Localized>
    );
  }

  const success = (
    <Localized
      id='batchactions-CopyFromLocale--success'
      vars={{ changedCount: changedCount ?? -1 }}
    >
      {'{ $changedCount } STRINGS COPIED'}
    </Localized>
  );

  return invalidCount ? (
    <>
      {success}
      {' · '}
      <Localized
        id='batchactions-CopyFromLocale--invalid-count'
        vars={{ invalidCount: invalidCount ?? -1 }}
      >
        {'{ $invalidCount } STRINGS SKIPPED'}
      </Localized>
    </>
  ) : (
    success
  );
}
