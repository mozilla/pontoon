import React, { useContext } from 'react';

import type {
  ComposedMachineryTranslation,
  MachineryTranslation,
} from '~/api/machinery';
import { EntityView } from '~/context/EntityView';
import { Locale } from '~/context/Locale';
import { SearchData } from '~/context/SearchData';
import { useLLMTranslation } from '~/context/TranslationContext';

import { AIRefine } from './source/AIRefine';
import { GoogleTranslation } from './source/GoogleTranslation';
import { OpenAITranslation } from './source/OpenAITranslation';
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

  // The quality score is rendered ahead of this list and always comes from the
  // Translation Memory match, so that badge has to lead for the two to read as
  // one. A stable sort leaves the rest in arrival order.
  const ordered = [...translation.sources].sort(
    (a, b) =>
      Number(b === 'translation-memory') - Number(a === 'translation-memory'),
  );

  for (const source of ordered) {
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
        sources.push(<GoogleTranslation key={source} />);
        break;
      case 'openai-chatgpt':
        sources.push(<OpenAITranslation key={source} />);
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

  return (
    <ul className='sources'>
      {sources}
      {!composed && isOpenAIChatGPTSupported && (
        <SingleAIRefine translation={translation as MachineryTranslation} />
      )}
    </ul>
  );
}

/**
 * Offered for Google Translate output only: the refinement prompt takes one
 * machine translation as its reference, and that is the one the panel has.
 */
function SingleAIRefine({
  translation,
}: {
  translation: MachineryTranslation;
}): React.ReactElement<'li'> | null {
  const locale = useContext(Locale);
  const { entity } = useContext(EntityView);
  const { query } = useContext(SearchData);
  const getLLMTranslationState = useLLMTranslation();
  const { selectedOption, transformLLMTranslation, restoreOriginal } =
    getLLMTranslationState(translation);

  if (!translation.sources.includes('google-translate')) {
    return null;
  }

  return (
    <AIRefine
      selectedOption={selectedOption}
      onSelect={(characteristic) =>
        transformLLMTranslation(
          translation,
          characteristic,
          locale.code,
          // A Concordance search result is not the entity being translated, so
          // its context would be the wrong context to refine against.
          query ? undefined : entity.pk,
        )
      }
      onRestore={() => restoreOriginal(translation)}
    />
  );
}
