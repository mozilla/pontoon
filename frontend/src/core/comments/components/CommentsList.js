/* @flow */

import * as React from 'react';

import './CommentsList.css';

import { Comment, AddComment } from 'core/comments';

import type { TranslationComment } from 'core/api';
import type { UserState } from 'core/user';
import type { HistoryTranslation } from 'modules/history'
import type { TeamCommentState } from 'modules/teamcomments';


type Props = {|
    comments: Array<TranslationComment>,
    teamComments: TeamCommentState,
    translation: HistoryTranslation,
    user: UserState,
    canComment: boolean,
    addComment: (string, ?number) => void,
|};


export default function CommentsList(props: Props) {
    const {
        comments,
        teamComments,
        translation,
        user,
        canComment,
        addComment,
    } = props;

    if (!comments && !teamComments) {
        return null;
    }

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
                    user={ translation.user }
                    username={ translation.username }
                    imageURL={ translation.userGravatarUrlSmall}
                    translation={ translation.pk }
                    addComment={ addComment }
                />
            }
        </div>
    }

    if (teamComments) {
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
