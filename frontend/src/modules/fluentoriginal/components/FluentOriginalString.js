/* @flow */

import * as React from 'react';

import { fluent } from 'core/utils';

import RichString from './RichString';
import SimpleString from './SimpleString';
import SourceString from './SourceString';

import ContextIssueButton from 'modules/entitydetails/components/ContextIssueButton';

import type { Entity } from 'core/api';
import type { TermState } from 'core/term';

type Props = {|
    +entity: Entity,
    +terms: TermState,
    +showContextIssueButton: boolean,
    +handleClickOnPlaceable: (
        SyntheticMouseEvent<HTMLParagraphElement>,
    ) => void,
    +openTeamComments: () => void,
|};

/**
 * Show the original string of a Fluent entity.
 *
 * Based on the syntax type of the string, render it as a simple string preview,
 * as a rich UI or as the original, untouched string.
 */
export default function FluentOriginalString(props: Props) {
    const message = fluent.parser.parseEntry(props.entity.original);
    const syntax = fluent.getSyntaxType(message);

    if (syntax === 'simple') {
        return (
            <>
                {!props.showContextIssueButton ? null : (
                    <ContextIssueButton
                        openTeamComments={props.openTeamComments}
                    />
                )}
                <SimpleString
                    entity={props.entity}
                    terms={props.terms}
                    handleClickOnPlaceable={props.handleClickOnPlaceable}
                />
            </>
        );
    }

    if (syntax === 'rich') {
        return (
            <div className='container'>
                <RichString
                    entity={props.entity}
                    terms={props.terms}
                    handleClickOnPlaceable={props.handleClickOnPlaceable}
                />
                {!props.showContextIssueButton ? null : (
                    <ContextIssueButton
                        openTeamComments={props.openTeamComments}
                    />
                )}
            </div>
        );
    }

    // Complex, unsupported strings.
    return (
        <>
            {!props.showContextIssueButton ? null : (
                <ContextIssueButton openTeamComments={props.openTeamComments} />
            )}
            <SourceString
                entity={props.entity}
                terms={props.terms}
                handleClickOnPlaceable={props.handleClickOnPlaceable}
            />
        </>
    );
}
