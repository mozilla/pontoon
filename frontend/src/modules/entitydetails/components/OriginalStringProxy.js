/* @flow */

import * as React from 'react';

import { FluentOriginalString } from 'modules/fluentoriginal';

import ContextIssueButton from './ContextIssueButton';
import GenericOriginalString from './GenericOriginalString';

import type { Entity } from 'core/api';
import type { Locale } from 'core/locale';
import type { TermState } from 'core/term';

type Props = {|
    +entity: Entity,
    +locale: Locale,
    +pluralForm: number,
    +terms: TermState,
    +showContextIssueButton: boolean,
    +handleClickOnPlaceable: (
        SyntheticMouseEvent<HTMLParagraphElement>,
    ) => void,
    +openTeamComments: () => void,
|};

/**
 * Proxy for an OriginalString component based on the format of the entity.
 *
 * For Fluent strings ('ftl'), returns a Fluent-specific OriginalString
 * component. For everything else, return a generic OriginalString component.
 */
export default function OriginalStringProxy(props: Props) {
    if (props.entity.format === 'ftl') {
        return (
            <FluentOriginalString
                entity={props.entity}
                terms={props.terms}
                showContextIssueButton={props.showContextIssueButton}
                handleClickOnPlaceable={props.handleClickOnPlaceable}
                openTeamComments={props.openTeamComments}
            />
        );
    }

    return (
        <>
            {!props.showContextIssueButton ? null : (
                <ContextIssueButton openTeamComments={props.openTeamComments} />
            )}
            <GenericOriginalString
                entity={props.entity}
                locale={props.locale}
                pluralForm={props.pluralForm}
                terms={props.terms}
                handleClickOnPlaceable={props.handleClickOnPlaceable}
            />
        </>
    );
}
