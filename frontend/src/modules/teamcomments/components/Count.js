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

    const commentCount = teamComments.comments.length;
    const pinnedCommentCount = teamComments.comments.filter((comment) => {
        return comment.pinned === true;
    }).length;

    if (!commentCount && !pinnedCommentCount) {
        return null;
    }

    const pinned = !pinnedCommentCount ? null : (
        <span className='pinned'>{pinnedCommentCount}</span>
    );

    const commentTotal = !commentCount ? null : (
        <span>{commentCount - pinnedCommentCount}</span>
    );

    const plus =
        !commentCount || !pinnedCommentCount ? null : <span>{'+'}</span>;

    return (
        <span className='count'>
            {pinned}
            {plus}
            {commentTotal}
        </span>
    );
}
