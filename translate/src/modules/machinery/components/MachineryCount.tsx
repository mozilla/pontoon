import React, { useContext } from 'react';

import { MachineryTranslations } from '~/context/MachineryTranslations';
import { SearchData } from '~/context/SearchData';

export function MachineryCount(): React.ReactElement<'span'> | null {
  const { translations } = useContext(MachineryTranslations);
  const { results } = useContext(SearchData);

  let preferred = 0;
  for (const { sources } of translations) {
    if (sources.includes('translation-memory')) {
      preferred += 1;
    }
  }

  const machinery = translations.length + results.length;
  if (!machinery) {
    return null;
  }

  return preferred === 0 ? (
    <span className='count'>
      <span>{machinery}</span>
    </span>
  ) : (
    <span className='count'>
      <span className='preferred'>{preferred}</span>
      {preferred === machinery ? null : (
        <>
          <span>+</span>
          <span>{machinery - preferred}</span>
        </>
      )}
    </span>
  );
}
