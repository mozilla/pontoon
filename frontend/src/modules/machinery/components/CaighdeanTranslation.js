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
 * Show the translation source from Caighdean Machine Translation.
 */
export default function CaighdeanTranslation(props: Props) {
    const { source } = props;

    return <li>
        <Localized
            id= "machinery-CaighdeanTranslation--visit-caighdean"
            attrs={{ title: true }}
        >
            <a
                className="translation-source"
                href={ source.url }
                title="Visit Caighdean Machine Translation"
                target="_blank"
                rel="noopener noreferrer"
                onClick={ (e: SyntheticMouseEvent<>) => e.stopPropagation() }
            >
                <span>Caighdean</span>
            </a>
        </Localized>
    </li>
}
