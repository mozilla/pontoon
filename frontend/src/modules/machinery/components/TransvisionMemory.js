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
 * Show the translation source from Transvision.
 */
export default function TransvisionMemory(props: Props) {
    const { source} = props;

    return <li>
        <Localized
            id= "machinery-TransvisionMemory--visit-transvision"
            attrs={{ title: true }}
        >
            <a
                className="translation-source"
                href={ source.url }
                title="Visit Transvision"
                target="_blank"
                rel="noopener noreferrer"
                onClick={ (e: SyntheticMouseEvent<>) => e.stopPropagation() }
            >
                <span>Mozilla</span>
            </a>
        </Localized>
    </li>
}
