/* @flow */

import * as React from 'react';

import './CommentList.css';

import { Comment, AddComment } from 'core/comments';

import type { TranslationComment } from 'core/api';
import type { HistoryTranslation } from 'modules/history'


type Props = {|
    comments: Array<TranslationComment>,
    translation: HistoryTranslation,
    canComment: boolean,
    addComment: (string, number) => void,
|};


export default function CommentsList(props: Props) {
    const {
        comments,
        translation,
        canComment,
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
        { !canComment ? null :
            <AddComment
                user={ translation.user }
                username={ translation.username }
                imageURL={ translation.userGravatarUrlSmall}
                translationId={ translation.pk }
                addComment={ addComment }
            />
        }
    </div>
}
