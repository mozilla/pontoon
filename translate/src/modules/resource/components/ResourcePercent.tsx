import React from 'react';

import './ResourcePercent.css';

import type { Resource } from '../actions';

type Props = {
  resource: Resource;
};

/**
 * Render a resource item percentage.
 */
export function ResourcePercent({
  resource: { approvedStrings, stringsWithWarnings, totalStrings },
}: Props): React.ReactElement<'span'> {
  const percent =
    Math.floor(((approvedStrings + stringsWithWarnings) / totalStrings) * 100) +
    '%';
  return <span className='percent'>{percent}</span>;
}
