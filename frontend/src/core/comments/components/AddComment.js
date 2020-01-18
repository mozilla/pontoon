/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

import './AddComment.css';

import { UserAvatar } from 'core/user'

type Props = {|
    user: string,
    username: string,
    imageURL: string,
    translationId: number,
    addComment: (string, number) => void,
|};


export default function AddComments(props: Props) {
    const {
        user,
        username,
        imageURL,
        translationId,
        addComment,
    } = props;

    let commentInput: any = React.useRef();

    if (!user) {
        return null;
    }

    const submitComment = (event: SyntheticKeyboardEvent<>) => {
        event.preventDefault();
        const comment = commentInput.current.value;

        if (!comment) {
            return null;
        }

        addComment(comment, translationId);
        commentInput.current.value = '';
    };

    return <div className='comment add-comment'>
        <UserAvatar
            user={ user }
            username={ username }
            title=''
            imageUrl={ imageURL }
        />
        <form className='container' onSubmit={ submitComment }>
            <Localized
                id='comments-AddComment--input'
                attrs={{ placeholder: true }}
            >
                <input
                    type='text'
                    id='comment-input'
                    name='comment'
                    dir='auto'
                    placeholder={ `Write a comment ${'\u2026'}` }
                    ref={ commentInput }
                />
            </Localized>
        </form>
    </div>
}
