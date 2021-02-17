/* @flow */

import React from 'react';
import { Localized } from '@fluent/react';

type Props = {|
    projectName?: ?string,
    emptyList?: boolean,
|};

/**
 * Show the concordance search results from Pontoon's memory.
 */
export default function ConcordanceSearch(props: Props) {
    if (!props.projectName && !props.emptyList) {
        return null;
    }

    return (
        <li>
            <span className='translation-source'>
                {props.emptyList ? (
                    <Localized id='machinery-ConcordanceSearch--translation-memory'>
                        <span>TRANSLATION MEMORY</span>
                    </Localized>
                ) : (
                    <span>
                        {props.projectName && props.projectName.toUpperCase()}
                    </span>
                )}
            </span>
        </li>
    );
}
