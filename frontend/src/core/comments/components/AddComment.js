/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

import './AddComment.css';

import { UserAvatar } from 'core/user'

import type { NavigationParams } from 'core/navigation';

type Props = {|
    user: string,
    username: string,
    imageURL: string,
    parameters: ?NavigationParams,
    translation?: ?number,
    addComment: (string, ?number) => void,
|};


export default function AddComments(props: Props) {
    const {
        user,
        username,
        imageURL,
        parameters,
        translation,
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

    const handleOnKeyDown = (event: SyntheticKeyboardEvent<>) => {
        if (event.keyCode === 13 && event.shiftKey === false) {
            submitComment(event);
        }
    }

    const submitComment = (event: SyntheticEvent<>) => {
        event.preventDefault();
        const comment = commentInput.current.value;

        if (!comment) {
            return null;
        }

        addComment(comment, translation);

        commentInput.current.value = '';
        commentInput.current.rows = minRows;
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
                    autoFocus={ !parameters || parameters.project !== 'terminology' }
                    name='comment'
                    dir='auto'
                    placeholder={ `Write a comment…` }
                    rows={ minRows }
                    ref={ commentInput }
                    onChange={ handleOnChange }
                    onKeyDown={ handleOnKeyDown }
                />
            </Localized>
            <Localized
                id="comments-AddComment--submit-button"
                attrs={{ title: true }}
                elems={{ glyph: <i className="fa fa-paper-plane" /> }}
            >
                <button
                    className="submit-button"
                    title="Submit comment"
                    onClick={ submitComment }
                >
                    { '<glyph></glyph>' }
                </button>
            </Localized>
        </form>
    </div>
}
