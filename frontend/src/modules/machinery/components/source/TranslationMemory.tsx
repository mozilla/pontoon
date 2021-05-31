import * as React from 'react';
import { Localized } from '@fluent/react';

type Props = {
    itemCount?: number;
};

/**
 * Show the translation source from Pontoon's memory.
 */
export default function TranslationMemory(
    props: Props,
): React.ReactElement<'li'> {
    return (
        <li>
            <Localized
                id='machinery-TranslationMemory--pontoon-homepage'
                attrs={{ title: true }}
            >
                <a
                    className='translation-source'
                    href='/'
                    title='Pontoon Homepage'
                    target='_blank'
                    rel='noopener noreferrer'
                    onClick={(e: React.MouseEvent) => e.stopPropagation()}
                >
                    <Localized id='machinery-TranslationMemory--translation-memory'>
                        <span>TRANSLATION MEMORY</span>
                    </Localized>
                    {!props.itemCount ? null : (
                        <Localized
                            id='machinery-TranslationMemory--number-occurrences'
                            attrs={{ title: true }}
                        >
                            <sup title='Number of translation occurrences'>
                                {props.itemCount}
                            </sup>
                        </Localized>
                    )}
                </a>
            </Localized>
        </li>
    );
}
