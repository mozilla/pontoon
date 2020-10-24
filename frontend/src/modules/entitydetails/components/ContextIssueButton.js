/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

import './ContextIssueButton.css';

type Props = {|
    openTeamComments: () => void,
|};

export default function ContextIssueButton(props: Props) {
    const [isDisabled, setIsDisabled] = React.useState(false);

    const handleClick = () => {
        setIsDisabled(true);
        props.openTeamComments();

        setTimeout(() => {
            setIsDisabled(false);
        }, 3000);
    };
    return (
        <div className='source-string-comment'>
            <Localized id='entitydetails-ContextIssueButton--context-issue-button'>
                <button
                    className='context-issue-button'
                    onClick={handleClick}
                    disabled={isDisabled}
                >
                    {'REQUEST CONTEXT or REPORT ISSUE'}
                </button>
            </Localized>
        </div>
    );
}
