/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

import './ContextIssueButton.css';

type Props = {|
    openTeamComments: () => void,
|};

export default function ContextIssueButton(props: Props) {
    return (
        <div className='source-string-comment'>
            <Localized id='entitydetails-ContextIssueButton--context-issue-button'>
                <button
                    className='context-issue-button'
                    onClick={props.openTeamComments}
                >
                    {'REQUEST CONTEXT or REPORT ISSUE'}
                </button>
            </Localized>
        </div>
    );
}
