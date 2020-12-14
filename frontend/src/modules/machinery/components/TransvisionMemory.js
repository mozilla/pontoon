/* @flow */

import React from 'react';
import { Localized } from '@fluent/react';

import type { Locale } from 'core/locale';

export type Props = {|
    original: string,
    locale: Locale,
|};

/**
 * Show the translation source from Transvision.
 */
export default function TransvisionMemory(props: Props) {
    return (
        <li>
            <Localized
                id='machinery-TransvisionMemory--visit-transvision'
                attrs={{ title: true }}
            >
                <a
                    className='translation-source'
                    href={
                        'https://transvision.mozfr.org/?repo=global' +
                        '&recherche=' +
                        encodeURIComponent(props.original) +
                        '&locale=' +
                        props.locale.code
                    }
                    title='Visit Transvision'
                    target='_blank'
                    rel='noopener noreferrer'
                    onClick={(e: SyntheticMouseEvent<>) => e.stopPropagation()}
                >
                    <span>MOZILLA</span>
                </a>
            </Localized>
        </li>
    );
}
