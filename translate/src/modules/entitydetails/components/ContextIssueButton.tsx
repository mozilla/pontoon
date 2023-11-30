import React from 'react';
import { Localized } from '@fluent/react';

import './ContextIssueButton.css';

type Props = {
  openTeamComments: () => void;
};

export function ContextIssueButton(props: Props): React.ReactElement<'div'> {
  return (
    <Localized id='entitydetails-ContextIssueButton--context-issue-button'>
      <button className='context-issue-button' onClick={props.openTeamComments}>
        {'REQUEST CONTEXT or REPORT ISSUE'}
      </button>
    </Localized>
  );
}
