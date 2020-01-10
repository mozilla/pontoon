/* @flow */

import * as React from 'react';

import type { TranslationComment } from 'core/api';
import type { UserState } from 'core/user';
import type { HistoryTranslation } from 'modules/history'

import { Comment, AddComment } from 'core/comments';


type Props = {|
    comments: Array<TranslationComment>,
    user: UserState,
    isTranslator: boolean,
    translation: HistoryTranslation,
    addComment: (string, number) => void,
    deleteComment: (number) => void,
|};


export default function CommentsList(props: Props) {
    const {
        comments,
        user,
        isTranslator,
        translation,
        addComment,
        deleteComment,
    } = props;

    if (!comments) {
        return null;
    }

    return <div className='comments-list'>
        <ul>
            { comments.map(comment =>
                <Comment
                    comment={ comment }
                    key={ comment.id }
                    user={ user }
                    isTranslator={ isTranslator }
                    deleteComment={ deleteComment }
                />
            )}
        </ul>
        <AddComment
            user={ translation.user }
            username={ translation.username }
            imageURL={ translation.userGravatarUrlSmall}
            translationId={ translation.pk }
            addComment={ addComment }
        />
    </div>
}
