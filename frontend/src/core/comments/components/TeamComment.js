/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

import './CommentList.css'
import './TeamComment.css';

import { Comment, AddComment } from 'core/comments';

import type { Entity } from 'core/api';
import type { TeamCommentState } from 'core/comments';
import type { UserState } from 'core/user';

type Props = {|
    teamComments: TeamCommentState,
    user: UserState,
    entity: Entity,
    addComment: (string, number) => void,
|};


export default function TeamComment(props: Props) {
    const { teamComments, user, entity, addComment } = props;

    let canComment = user.isAuthenticated;

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

    return <div className='comments-list team-comments-list'>
        <ul>
            { teamComments.comments.map(comment =>
                <Comment
                    comment={ comment }
                    key={ comment.id }
                />
            )}
        </ul>
        { !canComment ? null :
            <AddComment
                user={ user.nameOrEmail }
                username={ user.username }
                imageURL={ user.gravatarURLSmall}
                id={ entity.pk }
                addComment={ addComment }
            />
        }
    </div>

}
