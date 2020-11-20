/* @flow */

import React from 'react';
import { Localized } from '@fluent/react';

/**
 * Show the translation source from Systran.
 */
export default function SystranTranslation() {
    return (
        <li>
            <Localized
                id='machinery-SystranTranslation--visit-systran'
                attrs={{ title: true }}
            >
                <a
                    className='translation-source'
                    href='https://translate.systran.net/translationTools'
                    title='VISIT SYSTRAN TRANSLATE'
                    target='_blank'
                    rel='noopener noreferrer'
                    onClick={(e: SyntheticMouseEvent<>) => e.stopPropagation()}
                >
                    <span>SYSYTRAN TRANSLATE</span>
                </a>
            </Localized>
        </li>
    );
}
