/* @flow */

import * as React from 'react';

import FluentTranslation from './FluentTranslation';
import GenericTranslation from './GenericTranslation';

type Props = {|
    content: ?string,
    diffTarget?: ?string,
    format: string,
    search?: ?string,
|};

export default class TranslationProxy extends React.Component<Props> {
    render() {
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
