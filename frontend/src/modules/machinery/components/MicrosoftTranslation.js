/* @flow */

import React from 'react';
import { Localized } from '@fluent/react';


type Props = {|
    source: {
        type: string,
        url: string,
    },
|};


/**
 * Show the translation source from Microsoft Translation.
 */
export default function MicrosoftTranslation(props: Props)  {
    const { source } = props;

    return <li>
        <Localized
            id= "machinery-MicrosoftTranslation--visit-bing"
            attrs={{ title: true }}
        >
            <a
                className="translation-source"
                href={ source.url }
                title="Visit Bing Translate"
                target="_blank"
                rel="noopener noreferrer"
                onClick={ (e: SyntheticMouseEvent<>) => e.stopPropagation() }
            >
                <span>Microsoft Translator</span>
            </a>
        </Localized>
    </li>
}
