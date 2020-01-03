/* @flow */

import * as React from 'react';

import type { TranslationComment } from 'core/api';

import { Comment, AddComment } from 'core/comments';


type Props = {|
    comments: Array<TranslationComment>,
|};


export default function CommentsList(props: Props) {
    const { comments } = props;

    if (!comments) {
        return null;
    }

    return <div className='comment-list'>
        <ul>
            { comments.map(comment =>
                <Comment
                    comment={ comment }
                    key={ comment.id }
                />
            )}
        </ul>
        <AddComment />
    </div>
}
