import * as React from 'react';

import FluentTranslation from './FluentTranslation';
import GenericTranslation from './GenericTranslation';

type Props = {
    content: string | null | undefined;
    diffTarget?: string | null | undefined;
    format: string;
    search?: string | null | undefined;
};

export default function TranslationProxy({
    format,
    ...props
}: Props): null | React.ReactElement<React.ElementType> {
    if (!props.content) {
        return null;
    }

    const Translation =
        format === 'ftl' ? FluentTranslation : GenericTranslation;
    return <Translation {...props} />;
}
