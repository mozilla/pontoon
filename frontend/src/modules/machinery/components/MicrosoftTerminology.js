/* @flow */

import React from 'react';
import { Localized } from '@fluent/react';

import type { Locale } from 'core/locale';

type Props = {|
    original: string,
    locale: Locale,
|};

/**
 * Show the translation source from Microsoft Terminology.
 */
export default function MicrosoftTerminology(props: Props) {
    return (
        <li>
            <Localized
                id='machinery-MicrosoftTerminology--visit-microsoft'
                attrs={{ title: true }}
            >
                <a
                    className='translation-source'
                    href={
                        'https://www.microsoft.com/Language/en-US/Search.aspx?sString=' +
                        props.original +
                        '&langID=' +
                        props.locale.msTerminologyCode
                    }
                    title={
                        'Visit Microsoft Terminology Service API.\n' +
                        '© 2018 Microsoft Corporation. All rights reserved.'
                    }
                    target='_blank'
                    rel='noopener noreferrer'
                    onClick={(e: SyntheticMouseEvent<>) => e.stopPropagation()}
                >
                    <span>MICROSOFT</span>
                </a>
            </Localized>
        </li>
    );
}
