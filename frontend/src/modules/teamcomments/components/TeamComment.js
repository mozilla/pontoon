/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

import './TeamComment.css';

import { AddComment, CommentsList } from 'core/comments';

import type { UserState } from 'core/user';
import type { TeamCommentState } from 'modules/teamcomments';

type Props = {|
    teamComments: TeamCommentState,
    user: UserState,
    addComment: (string, ?number) => void,
|};


export default function TeamComment(props: Props) {
    const { teamComments, user, addComment } = props;

    let canComment = user.isAuthenticated;

    if (!teamComments.comments) {
        return null;
    }

    if (!teamComments.comments.length) {
        return <section>
            <div className="no-team-comments">
                <Localized id="entitydetails-Helpers--no-comments">
                    <p>No comments available.</p>
                </Localized>
            </div>
            <div className='comments-list team-comments-list'>
                { !canComment ? null :
                    <AddComment
                        user={ user.nameOrEmail }
                        username={ user.username }
                        imageURL={ user.gravatarURLSmall}
                        addComment={ addComment }
                    />
                }
            </div>
        </section>
    }

    return (
        <CommentsList
            teamComments={ teamComments }
            user={ user }
            canComment={ canComment }
            addComment={ addComment }
        />
    )

}
