/* @flow */

import React from 'react';
import { Localized } from '@fluent/react';

/**
 * Show the translation source from Google Translate.
 */
export default function GoogleTranslation() {
    return (
        <li>
            <Localized
                id='machinery-GoogleTranslation--visit-google'
                attrs={{ title: true }}
            >
                <a
                    className='translation-source'
                    href='https://translate.google.com/'
                    title='Visit Google Translate'
                    target='_blank'
                    rel='noopener noreferrer'
                    onClick={(e: SyntheticMouseEvent<>) => e.stopPropagation()}
                >
                    <span>Google Translate</span>
                </a>
            </Localized>
        </li>
    );
}
