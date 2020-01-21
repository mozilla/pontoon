/* @flow */

import * as React from 'react';

import './CommentList.css';

import { Comment, AddComment } from 'core/comments';

import type { TranslationComment } from 'core/api';
import type { HistoryTranslation } from 'modules/history'
import type { UserState } from 'core/user';


type Props = {|
    comments: Array<TranslationComment>,
    translation: HistoryTranslation,
    isTranslator: boolean,
    user: UserState,
    addComment: (string, number) => void,
|};


export default function CommentsList(props: Props) {
    const {
        comments,
        translation,
        isTranslator,
        user,
        addComment,
    } = props;

    if (!comments) {
        return null;
    }

    // Does the currently logged in user own this translation?
    const ownTranslation = (
        user && user.username &&
        user.username === translation.username
    );

    const canComment = (isTranslator || ownTranslation);

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
