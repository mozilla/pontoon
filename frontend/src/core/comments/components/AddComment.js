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
    const [rows, setRows] = React.useState(1);
    const minRows = 1;
    const maxRows = 3;

    if (!user) {
        return null;
    }

    const handleKeyUp = (event: SyntheticKeyboardEvent<HTMLTextAreaElement>) => {
        if (event.keyCode === 13 && event.shiftKey === false) {
            event.preventDefault();
            submitComment(event);
        }
        else {
            const textAreaLineHeight = 24;
            const previousRows = commentInput.current.rows;
            commentInput.current.rows = minRows;

            const currentRows = Math.trunc(commentInput.current.scrollHeight / textAreaLineHeight);

            if (currentRows === previousRows) {
                commentInput.current.rows = currentRows;
            }

            if (currentRows >= maxRows) {
                commentInput.current.rows = maxRows;
            }

            currentRows < maxRows ? setRows(currentRows) : setRows(maxRows);
        }
    }

    const submitComment = (event: SyntheticKeyboardEvent<>) => {
        event.preventDefault();
        const comment = commentInput.current.value;

        if (!comment) {
            return null;
        }

        addComment(comment, translationId);
        commentInput.current.value = '';
        commentInput.current.rows = minRows;
    };

    return <div className='comment add-comment'>
        <UserAvatar
            user={ user }
            username={ username }
            title=''
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
                    rows={ rows }
                    ref={ commentInput }
                    onKeyUp={ handleKeyUp }
                />
            </Localized>
        </form>
    </div>
}
