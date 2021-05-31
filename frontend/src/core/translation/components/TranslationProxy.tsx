import * as React from 'react';

import FluentTranslation from './FluentTranslation';
import GenericTranslation from './GenericTranslation';

type Props = {
    content: string | null | undefined;
    diffTarget?: string | null | undefined;
    format: string;
    search?: string | null | undefined;
};

export default class TranslationProxy extends React.Component<Props> {
    render(): null | React.ReactElement<React.ElementType> {
        const { content, diffTarget, format, search } = this.props;

        if (!content) {
            return null;
        }

        if (format === 'ftl') {
            return (
                <FluentTranslation
                    content={content}
                    diffTarget={diffTarget}
                    search={search}
                />
            );
        }

        return (
            <GenericTranslation
                content={content}
                diffTarget={diffTarget}
                search={search}
            />
        );
    }
}
