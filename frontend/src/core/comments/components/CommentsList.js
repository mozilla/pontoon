/* @flow */

import * as React from 'react';

import './CommentList.css';

import type { TranslationComment } from 'core/api';
import type { HistoryTranslation } from 'modules/history'

import { Comment, AddComment } from 'core/comments';


type Props = {|
    comments: Array<TranslationComment>,
    translation: HistoryTranslation,
    addComment: (string, number) => void,
|};


export default function CommentsList(props: Props) {
    const {
        comments,
        translation,
        addComment,
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
