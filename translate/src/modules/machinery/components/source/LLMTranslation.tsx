import React from 'react';
import { Localized } from '@fluent/react';

/**
 * Show the translation source for an LLM-generated suggestion.
 */
export function LLMTranslation(): React.ReactElement<'li'> {
  return (
    <li>
      <Localized id='machinery-LLMTranslation--translation-source'>
        <span className='translation-source'>OPENAI CHATGPT</span>
      </Localized>
    </li>
  );
}
