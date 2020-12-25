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
                <a
                    className='translation-source'
                    href='/'
                    title='Pontoon Homepage'
                    target='_blank'
                    rel='noopener noreferrer'
                    onClick={(e: SyntheticMouseEvent<>) => e.stopPropagation()}
                >
                    {!props.projectName ? (
                        <Localized id='machinery-ConcordanceSearch--translation-memory'>
                            <span>TRANSLATION MEMORY</span>
                        </Localized>
                    ) : (
                        <span>{props.projectName.toUpperCase()}</span>
                    )}
                </a>
            </Localized>
        </li>
    );
}
