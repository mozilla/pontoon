import * as React from 'react';
import { Localized } from '@fluent/react';

/**
 * Show the translation source from Google Translate.
 */
export default function GoogleTranslation(): React.ReactElement<'li'> {
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
                    onClick={(e: React.MouseEvent) => e.stopPropagation()}
                >
                    <span>GOOGLE TRANSLATE</span>
                </a>
            </Localized>
        </li>
    );
}
