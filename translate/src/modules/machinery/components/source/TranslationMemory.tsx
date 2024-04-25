import React from 'react';
import { Localized } from '@fluent/react';

type Props = {
  itemCount?: number;
};

/**
 * Show the translation source from Pontoon's memory.
 */
export function TranslationMemory(props: Props): React.ReactElement<'li'> {
  return (
    <li>
      <span>
        <Localized id='machinery-TranslationMemory--translation-source'>
          <span className='translation-source'>TRANSLATION MEMORY</span>
        </Localized>
        {!props.itemCount ? null : (
          <Localized
            id='machinery-TranslationMemory--number-occurrences'
            attrs={{ title: true }}
          >
            <sup title='Number of translation occurrences'>
              {props.itemCount}
            </sup>
          </Localized>
        )}
      </span>
    </li>
  );
}
