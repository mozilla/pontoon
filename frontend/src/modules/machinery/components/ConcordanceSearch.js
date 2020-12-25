/* @flow */

import * as React from 'react';
import { useSelector } from 'react-redux';

import { GenericTranslation } from 'core/translation';

import TranslationSource from './TranslationSource';

import type { MachineryTranslation } from 'core/api';

type Props = {|
    sourceString: string,
    translation: MachineryTranslation,
|};

export default function ConcordanceSearch(props: Props) {
    const locale = useSelector((state) => state.locale);
    const { sourceString, translation } = props;

    return (
        <>
            <header>
                <TranslationSource translation={translation} locale={locale} />
            </header>
            <p className='original'>
                <GenericTranslation
                    content={translation.original}
                    search={sourceString}
                />
            </p>
            <p
                className='suggestion'
                dir={locale.direction}
                data-script={locale.script}
                lang={locale.code}
            >
                <GenericTranslation
                    content={translation.translation}
                    search={sourceString}
                />
            </p>
        </>
    );
}
