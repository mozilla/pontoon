import * as React from 'react';

import { fluent } from 'core/utils';

import RichString from './RichString';
import SimpleString from './SimpleString';
import SourceString from './SourceString';

import type { Entity } from 'core/api';
import type { TermState } from 'core/term';

type Props = {
    readonly entity: Entity;
    readonly terms: TermState;
    readonly handleClickOnPlaceable: (
        event: React.MouseEvent<HTMLParagraphElement>,
    ) => void;
};

/**
 * Show the original string of a Fluent entity.
 *
 * Based on the syntax type of the string, render it as a simple string preview,
 * as a rich UI or as the original, untouched string.
 */
export default function FluentOriginalString(
    props: Props,
): React.ReactElement<any> {
    const message = fluent.parser.parseEntry(props.entity.original);
    const syntax = fluent.getSyntaxType(message);

    if (syntax === 'simple') {
        return (
            <SimpleString
                entity={props.entity}
                terms={props.terms}
                handleClickOnPlaceable={props.handleClickOnPlaceable}
            />
        );
    }

    if (syntax === 'rich') {
        return (
            <RichString
                entity={props.entity}
                terms={props.terms}
                handleClickOnPlaceable={props.handleClickOnPlaceable}
            />
        );
    }

    // Complex, unsupported strings.
    return (
        <SourceString
            entity={props.entity}
            terms={props.terms}
            handleClickOnPlaceable={props.handleClickOnPlaceable}
        />
    );
}
