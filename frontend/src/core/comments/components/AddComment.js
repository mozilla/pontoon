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

    const commentInput: any = React.useRef();
    const minRows = 1;
    const maxRows = 6;

    if (!user) {
        return null;
    }

    const handleOnChange = () => {
        const textAreaLineHeight = 24;
        commentInput.current.rows = minRows;

        const currentRows = Math.trunc(commentInput.current.scrollHeight / textAreaLineHeight);

        if (currentRows < maxRows) {
            commentInput.current.rows = currentRows;
        }
        else {
            commentInput.current.rows = maxRows;
        }
    }

    const submitComment = (event: SyntheticKeyboardEvent<>) => {
        if (event.keyCode === 13 && event.shiftKey === false) {
            event.preventDefault();
            const comment = commentInput.current.value;

            if (!comment) {
                return null;
            }

            addComment(comment, translationId);
            commentInput.current.value = '';
            commentInput.current.rows = minRows;
        }
    };

    return <div className='comment add-comment'>
        <UserAvatar
            username={ username }
            imageUrl={ imageURL }
        />
        <form className='container'>
            <Localized
                id='comments-AddComment--input'
                attrs={{ placeholder: true }}
            >
                <textarea
                    id='comment-input'
                    name='comment'
                    dir='auto'
                    placeholder={ `Write a comment…` }
                    rows={ minRows }
                    ref={ commentInput }
                    onChange={ handleOnChange }
                    onKeyDown={ submitComment }
                />
            </Localized>
        </form>
    </div>
}
