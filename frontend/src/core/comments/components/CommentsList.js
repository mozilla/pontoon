/* @flow */

import * as React from 'react';

import type { TranslationComment } from 'core/api';
import type { UserState } from 'core/user';
import type { HistoryTranslation } from 'modules/history'

import { Comment, AddComment } from 'core/comments';


type Props = {|
    comments: Array<TranslationComment>,
    user: UserState,
    canReview: boolean,
    translation: HistoryTranslation,
    deleteComment: (number) => void,
|};


export default function CommentsList(props: Props) {
    const {
        comments,
        user,
        canReview,
        translation,
        deleteComment,
    } = props;

    if (!comments) {
        return null;
    }

    return <div className='comment-list'>
        <ul>
            { comments.map(comment =>
                <Comment
                    comment={ comment }
                    key={ comment.id }
                    user={ user }
                    canReview={ canReview }
                    deleteComment={ deleteComment }
                />
            )}
        </ul>
        <AddComment
            user={ translation.user }
            username={ translation.username }
            imageURL={ translation.userGravatarUrlSmall}
        />
    </div>
}
