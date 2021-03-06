/* @flow */

import type {Element} from "React";import React from 'react';
import { Localized } from '@fluent/react';

/**
 * Show the translation source from Microsoft Translation.
 */
export default function MicrosoftTranslation(): Element<"li"> {
    return (
        <li>
            <Localized
                id='machinery-MicrosoftTranslation--visit-bing'
                attrs={{ title: true }}
            >
                <a
                    className='translation-source'
                    href='https://www.bing.com/translator'
                    title='Visit Microsoft Translator'
                    target='_blank'
                    rel='noopener noreferrer'
                    onClick={(e: SyntheticMouseEvent<>) => e.stopPropagation()}
                >
                    <span>MICROSOFT TRANSLATOR</span>
                </a>
            </Localized>
        </li>
    );
}
