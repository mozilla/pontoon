import * as React from 'react';

import type { MachineryTranslation } from '~/core/api';
import type { Locale } from '~/core/locale';

import GoogleTranslation from './source/GoogleTranslation';
import MicrosoftTranslation from './source/MicrosoftTranslation';
import SystranTranslation from './source/SystranTranslation';
import MicrosoftTerminology from './source/MicrosoftTerminology';
import CaighdeanTranslation from './source/CaighdeanTranslation';
import TranslationMemory from './source/TranslationMemory';

type Props = {
    translation: MachineryTranslation;
    locale: Locale;
};

/**
 * Shows a list of translation sources.
 */
export function TranslationSource({
    translation,
    locale,
}: Props): React.ReactElement<'ul'> {
    const sources: React.ReactElement<'li'>[] = [];
    const seen: string[] = [];
    for (const source of translation.sources) {
        if (seen.includes(source)) continue;
        seen.push(source);
        switch (source) {
            case 'translation-memory':
                sources.push(
                    <TranslationMemory
                        itemCount={translation.itemCount}
                        key={source}
                    />,
                );
                break;
            case 'google-translate':
                sources.push(<GoogleTranslation key={source} />);
                break;
            case 'microsoft-translator':
                sources.push(<MicrosoftTranslation key={source} />);
                break;
            case 'systran-translate':
                sources.push(<SystranTranslation key={source} />);
                break;
            case 'microsoft-terminology':
                sources.push(
                    <MicrosoftTerminology
                        original={translation.original}
                        locale={locale}
                        key={source}
                    />,
                );
                break;
            case 'caighdean':
                sources.push(<CaighdeanTranslation key={source} />);
                break;
        }
    }

    return <ul className='sources'>{sources}</ul>;
}
