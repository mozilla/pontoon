/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

import './CommentList.css'
import './TeamComment.css';

import { Comment } from 'core/comments';

import type { TeamCommentState } from 'core/comments';

type Props = {|
    teamComments: TeamCommentState,
|};


export default function TeamComment(props: Props) {
    const { teamComments } = props;

    if (!teamComments.comments) {
        return null;
    }

    if (!teamComments.comments.length) {
        return <section className="no-team-comments">
            <Localized id="entitydetails-Helpers--no-comments">
                <p>No comments available.</p>
            </Localized>
        </section>
    }

    return <div className='comments-list team-comment-list'>
        <ul>
            { teamComments.comments.map(comment =>
                <Comment
                    comment={ comment }
                    key={ comment.id }
                />
            )}
        </ul>
    </div>

}
