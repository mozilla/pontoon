/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

import './CommentsList.css';

import { Comment, AddComment } from 'core/comments';

import type { TranslationComment } from 'core/api';
import type { UserState } from 'core/user';
import type { HistoryTranslation } from 'modules/history';
import type { TeamCommentState } from 'modules/commentslist';

type Props = {|
    teamComments: TeamCommentState,
    user: UserState,
    comments: Array<TranslationComment>,
    translation: HistoryTranslation,
    addComment: (string, ?number) => void,
|};


export default function CommentsList(props: Props) {
    const {
        teamComments,
        user,
        comments,
        translation,
        addComment,
    } = props;

    let canComment = user.isAuthenticated;

    if (comments) {
        return <div className='comments-list'>
            <ul>
                { comments.map(comment =>
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
                    imageURL={ user.gravatarURLSmall }
                    translation={ translation.pk }
                    addComment={ addComment }
                />
            }
        </div>
    }

    if (teamComments) {
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
                            imageURL={ user.gravatarURLSmall }
                            addComment={ addComment }
                        />
                    }
                </div>
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
                    addComment={ addComment }
                />
            }
        </div>
    }
}
