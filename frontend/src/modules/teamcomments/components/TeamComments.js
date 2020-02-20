/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

import './TeamComments.css';

import { AddComment, CommentsList } from 'core/comments';

import type { UserState } from 'core/user';
import type { TeamCommentState } from 'modules/teamcomments';

type Props = {|
    teamComments: TeamCommentState,
    user: UserState,
    addComment: (string, ?number) => void,
|};


export default function TeamComments(props: Props) {
    const { teamComments, user, addComment } = props;

    let canComment = user.isAuthenticated;
    const comments = teamComments.comments;

    if (!comments) {
        return null;
    }

    if (!comments.length) {
        return <section className="team-comments">
            { !canComment ?
                <div className="no-team-comments">
                    <Localized id="entitydetails-Helpers--no-comments">
                        <p>No comments available.</p>
                    </Localized>
                </div>
                :
                <section className="team-comments">
                    <CommentsList
                        comments={ comments }
                        user={ user }
                        canComment={ canComment }
                        addComment={ addComment }
                    />
                </section>
            }
        </section>
    }

    return <section className="team-comments">
        <CommentsList
            comments={ comments }
            user={ user }
            canComment={ canComment }
            addComment={ addComment }
        />
    </section>

}
