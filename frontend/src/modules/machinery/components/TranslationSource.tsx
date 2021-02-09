import React from 'react';

import { MachineryTranslation } from 'core/api';
import { Locale } from 'core/locale';

import GoogleTranslation from './GoogleTranslation';
import MicrosoftTranslation from './MicrosoftTranslation';
import SystranTranslation from './SystranTranslation';
import MicrosoftTerminology from './MicrosoftTerminology';
import CaighdeanTranslation from './CaighdeanTranslation';
import TranslationMemory from './TranslationMemory';

type Props = {
    translation: MachineryTranslation;
    locale: Locale;
};

/**
 * Shows a list of translation sources.
 */
export default function TranslationSource({ translation, locale }: Props) {
    const translationSource = translation.sources.map((source, index) => {
        switch (source) {
            case 'translation-memory':
                return (
                    <TranslationMemory
                        itemCount={translation.itemCount}
                        key={index}
                    />
                );
            case 'google-translate':
                return <GoogleTranslation key={index} />;
            case 'microsoft-translator':
                return <MicrosoftTranslation key={index} />;
            case 'systran-translate':
                return <SystranTranslation key={index} />;
            case 'microsoft-terminology':
                return (
                    <MicrosoftTerminology
                        original={translation.original}
                        locale={locale}
                        key={index}
                    />
                );
            case 'caighdean':
                return <CaighdeanTranslation key={index} />;
            default:
                return null;
        }
    });

    return <ul className='sources'>{translationSource}</ul>;
}
