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
 * Show the translation source from Google Translate.
 */
export default function GoogleTranslation(props: Props) {
    const { source } = props;

    return <li>
        <Localized
            id= "machinery-GoogleTranslation--visit-google"
            attrs={{ title: true }}
        >
            <a
                className="translation-source"
                href={ source.url }
                title="Visit Google Translate"
                target="_blank"
                rel="noopener noreferrer"
                onClick={ (e: SyntheticMouseEvent<>) => e.stopPropagation() }
            >
                <span>Google Translate</span>
            </a>
        </Localized>
    </li>
}
