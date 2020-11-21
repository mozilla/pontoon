/* @flow */

import React from 'react';
import { Localized } from '@fluent/react';

/**
 * Show the translation source from Caighdean Machine Translation.
 */
export default function CaighdeanTranslation() {
    return (
        <li>
            <Localized
                id='machinery-CaighdeanTranslation--visit-caighdean'
                attrs={{ title: true }}
            >
                <a
                    className='translation-source'
                    href='https://github.com/kscanne/caighdean'
                    title='Visit Caighdean Machine Translation'
                    target='_blank'
                    rel='noopener noreferrer'
                    onClick={(e: SyntheticMouseEvent<>) => e.stopPropagation()}
                >
                    <span>CAIGHDEAN</span>
                </a>
            </Localized>
        </li>
    );
}
