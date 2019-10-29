/* @flow */

import React from 'react';

import type { MachineryTranslation } from 'core/api';

import GoogleTranslation from './GoogleTranslation';
import MicrosoftTranslation from './MicrosoftTranslation';
import MicrosoftTerminology from './MicrosoftTerminology';
import TransvisionMemory from './TransvisionMemory';
import CaighdeanTranslation from './CaighdeanTranslation';
import TranslationMemory from './TranslationMemory';


type Props = {|
    translation: MachineryTranslation,
|};


/**
 * Shows a list of translation sources.
 */
export default function TranslationSource(props: Props) {
        const { translation } = props;

        const translationSource =
            translation.sources.map((source, index) => {
                switch (source.type) {
                    case 'translation-memory':
                        return <TranslationMemory
                            itemCount={ source.itemCount }
                            key={ index }
                        />;
                    case 'google-translate':
                        return <GoogleTranslation
                            key={ index }
                        />;
                    case 'microsoft-translator':
                        return <MicrosoftTranslation
                            key={ index }
                        />;
                    case 'microsoft-terminology':
                        return <MicrosoftTerminology
                            sourceString={ source.sourceString }
                            localeCode={ source.localeCode }
                            key={ index }
                        />;
                    case 'transvision':
                        return <TransvisionMemory
                            sourceString={ source.sourceString }
                            localeCode={ source.localeCode }
                            key={ index }
                        />;
                    case 'caighdean':
                        return <CaighdeanTranslation
                            key={ index }
                        />;
                    default:
                        return null;
                }
            });

        return  <ul className="sources">
            { translationSource }
        </ul>;
}
