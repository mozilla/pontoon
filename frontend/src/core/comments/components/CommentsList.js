/* @flow */

import * as React from 'react';

import './CommentsList.css';

import { Comment, AddComment } from 'core/comments';

import type { TranslationComment } from 'core/api';
import type { UserState } from 'core/user';
import type { HistoryTranslation } from 'modules/history'


type Props = {|
    comments: Array<TranslationComment>,
    translation?: HistoryTranslation,
    user: UserState,
    canComment: boolean,
    addComment: (string, ?number) => void,
|};


export default function CommentsList(props: Props) {
    const {
        comments,
        translation,
        user,
        canComment,
        addComment,
    } = props;

    const translationId = translation ? translation.pk : null;

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
                imageURL={ user.gravatarURLSmall}
                translation={ translationId }
                addComment={ addComment }
            />
        }
    </div>
}
