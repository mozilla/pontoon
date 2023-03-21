import React from 'react';

import type { TermState } from '../reducer';

type Props = {
  terms: TermState;
};

export function TermCount(props: Props): null | React.ReactElement<'span'> {
  const { terms } = props;

  if (terms.fetching || !terms.terms) {
    return null;
  }

  const termCount = terms.terms.length;

  return <span className='count'>{termCount}</span>;
}
