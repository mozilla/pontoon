/* @flow */

import React from 'react';
import { Localized } from '@fluent/react';

type Props = {|
    projectName?: ?string,
|};

/**
 * Show the concordance search results from Pontoon's memory.
 */
export default function ConcordanceSearch(props: Props) {
    return (
        <li>
            <Localized
                id='machinery-ConcordanceSearch--pontoon-homepage'
                attrs={{ title: true }}
            >
                <span className='translation-source'>
                    {!props.projectName ? (
                        <Localized id='machinery-ConcordanceSearch--translation-memory'>
                            <span>TRANSLATION MEMORY</span>
                        </Localized>
                    ) : (
                        <span>{props.projectName.toUpperCase()}</span>
                    )}
                </span>
            </Localized>
        </li>
    );
}
