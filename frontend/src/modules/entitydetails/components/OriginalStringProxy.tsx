import * as React from 'react';

import { FluentOriginalString } from 'modules/fluentoriginal';

import GenericOriginalString from './GenericOriginalString';

import type { Entity } from 'core/api';
import type { Locale } from 'core/locale';
import type { TermState } from 'core/term';

type Props = {
    readonly entity: Entity;
    readonly locale: Locale;
    readonly pluralForm: number;
    readonly terms: TermState;
    readonly handleClickOnPlaceable: (
        event: React.MouseEvent<HTMLParagraphElement>,
    ) => void;
};

/**
 * Proxy for an OriginalString component based on the format of the entity.
 *
 * For Fluent strings ('ftl'), returns a Fluent-specific OriginalString
 * component. For everything else, return a generic OriginalString component.
 */
export default function OriginalStringProxy(
    props: Props,
): React.ReactElement<any> {
    if (props.entity.format === 'ftl') {
        return (
            <FluentOriginalString
                entity={props.entity}
                terms={props.terms}
                handleClickOnPlaceable={props.handleClickOnPlaceable}
            />
        );
    }

    return (
        <GenericOriginalString
            entity={props.entity}
            locale={props.locale}
            pluralForm={props.pluralForm}
            terms={props.terms}
            handleClickOnPlaceable={props.handleClickOnPlaceable}
        />
    );
}
