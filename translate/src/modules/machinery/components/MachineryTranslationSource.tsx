import { Localized } from '@fluent/react';
import React from 'react';

import type {
  ComposedMachineryTranslation,
  MachineryTranslation,
} from '~/api/machinery';

import { GoogleTranslation } from './source/GoogleTranslation';
import { MicrosoftTranslation } from './source/MicrosoftTranslation';
import { MicrosoftTerminology } from './source/MicrosoftTerminology';
import { CaighdeanTranslation } from './source/CaighdeanTranslation';
import { TranslationMemory } from './source/TranslationMemory';

type Props = {
  translation: MachineryTranslation | ComposedMachineryTranslation;
  composed?: boolean;
};

/**
 * Shows a list of translation sources.
 */
export function MachineryTranslationSource({
  translation,
  composed,
}: Props): React.ReactElement<'ul'> {
  const sources: React.ReactElement<'li'>[] = [];
  const seen: string[] = [];

  const root = document.getElementById('root');
  const isOpenAIChatGPTSupported =
    root?.dataset.isOpenaiChatgptSupported === 'true';

  for (const source of translation.sources) {
    if (seen.includes(source)) {
      continue;
    }
    seen.push(source);
    switch (source) {
      case 'translation-memory':
        sources.push(
          <TranslationMemory
            itemCount={
              'itemCount' in translation ? translation.itemCount : undefined
            }
            key={source}
          />,
        );
        break;
      case 'google-translate':
        sources.push(
          composed ? (
            <li className='google-translation' key={source}>
              <Localized id='machinery-GoogleTranslation--translation-source'>
                <span className='translation-source'>GOOGLE TRANSLATE</span>
              </Localized>
            </li>
          ) : (
            <GoogleTranslation
              isOpenAIChatGPTSupported={isOpenAIChatGPTSupported}
              translation={translation as MachineryTranslation}
              key={source}
            />
          ),
        );
        break;
      case 'microsoft-translator':
        sources.push(<MicrosoftTranslation key={source} />);
        break;
      case 'microsoft-terminology':
        sources.push(<MicrosoftTerminology key={source} />);
        break;
      case 'caighdean':
        sources.push(<CaighdeanTranslation key={source} />);
        break;
    }
  }

  return <ul className='sources'>{sources}</ul>;
}
