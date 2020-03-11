/* @flow */

import * as React from 'react';

import type { TeamCommentState } from 'modules/teamcomments';


type Props = {|
    teamComments: TeamCommentState,
|};


export default function CommentCount(props: Props) {
    const { teamComments } = props;

    if (!teamComments.comments) {
        return null;
    }

    const commentCount = teamComments.comments.length;

    return <span className='count'>
        { commentCount }
    </span>;
}
