import { Localized } from '@fluent/react';
import React, { useContext } from 'react';

import { Locale } from '~/context/locale';

type Props = {
  original: string;
};

/**
 * Show the translation source from Microsoft Terminology.
 */
export default function MicrosoftTerminology({
  original,
}: Props): React.ReactElement<'li'> {
  const { msTerminologyCode } = useContext(Locale);
  const url = `https://www.microsoft.com/Language/en-US/Search.aspx?sString=${original}&langID=${msTerminologyCode}`;
  return (
    <li>
      <Localized
        id='machinery-MicrosoftTerminology--visit-microsoft'
        attrs={{ title: true }}
      >
        <a
          className='translation-source'
          href={url}
          title={
            'Visit Microsoft Terminology Service API.\n' +
            '© 2018 Microsoft Corporation. All rights reserved.'
          }
          target='_blank'
          rel='noopener noreferrer'
          onClick={(e: React.MouseEvent) => e.stopPropagation()}
        >
          <span>MICROSOFT</span>
        </a>
      </Localized>
    </li>
  );
}
