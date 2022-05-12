import React from 'react';

import type { MachineryState } from '~/modules/machinery';

type Props = {
  machinery: MachineryState;
};

export function MachineryCount({
  machinery: { searchResults, translations },
}: Props): null | React.ReactElement<'span'> {
  const machinery = translations.length + searchResults.length;

  if (!machinery) {
    return null;
  }

  const preferred = translations.reduce((count, item) => {
    if (item.sources.find((source) => source === 'translation-memory')) {
      return count + 1;
    }
    return count;
  }, 0);

  const remaining = machinery - preferred;

  return (
    <span className='count'>
      {preferred > 0 && <span className='preferred'>{preferred}</span>}
      {preferred > 0 && remaining > 0 && <span>+</span>}
      {remaining > 0 && <span>{remaining}</span>}
    </span>
  );
}
