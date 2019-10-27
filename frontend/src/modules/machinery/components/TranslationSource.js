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
        const {translation} = props;

        const translationSource =
            translation.sources.map((source, index) => {
                switch (source.type) {
                    case 'translation-memory':
                        return <TranslationMemory source={ source } key={ index }/>;
                    case 'google-translate':
                        return <GoogleTranslation source={ source } key={ index }/>;
                    case 'microsoft-translator':
                        return <MicrosoftTranslation source={ source } key={ index }/>;
                    case 'microsoft-terminology':
                        return <MicrosoftTerminology source={ source } key={ index }/>;
                    case 'transvision':
                        return <TransvisionMemory source={ source } key={ index }/>;
                    case 'caighdean':
                        return <CaighdeanTranslation source={ source } key={ index }/>;
                    default:
                        return null;
                }
            });

        return <div>{ translationSource }</div>
}
