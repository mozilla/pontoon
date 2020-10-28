/* @flow */

import * as React from 'react';

import type { TeamCommentState } from 'modules/teamcomments';

type Props = {|
    teamComments: TeamCommentState,
|};

export default function Count(props: Props) {
    const { teamComments } = props;

    if (teamComments.fetching || !teamComments.comments) {
        return null;
    }

    const pinnedCommentCount = teamComments.comments.filter((comment) => {
        return comment.pinned === true;
    }).length;
    const remainingCommentCount =
        teamComments.comments.length - pinnedCommentCount;

    if (!pinnedCommentCount && !remainingCommentCount) {
        return null;
    }

    const pinned = !pinnedCommentCount ? null : (
        <span className='pinned'>{pinnedCommentCount}</span>
    );

    const remaining = !remainingCommentCount ? null : (
        <span>{remainingCommentCount}</span>
    );

    const plus =
        !pinnedCommentCount || !remainingCommentCount ? null : (
            <span>{'+'}</span>
        );

    return (
        <span className='count'>
            {pinned}
            {plus}
            {remaining}
        </span>
    );
}
