import * as React from 'react';
import { Localized } from '@fluent/react';

/**
 * Show the translation source from Systran.
 */
export default function SystranTranslation(): React.ReactElement<'li'> {
    return (
        <li>
            <Localized
                id='machinery-SystranTranslation--visit-systran'
                attrs={{ title: true }}
            >
                <a
                    className='translation-source'
                    href='https://translate.systran.net/translationTools'
                    title='Visit Systran Translate'
                    target='_blank'
                    rel='noopener noreferrer'
                    onClick={(e: React.MouseEvent) => e.stopPropagation()}
                >
                    <span>SYSTRAN TRANSLATE</span>
                </a>
            </Localized>
        </li>
    );
}
